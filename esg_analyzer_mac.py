#!/usr/bin/env python3
"""
ESG COMPENSATION ANALYZER - Mac Standalone Version
Complete ESG compensation classifier in ONE file.
No external imports needed except pandas (optional).

USAGE:
    python3 esg_analyzer.py
"""

from typing import List, Dict, Any, Optional
import re
import json

# ===========================================================================
# ESG COMPENSATION CLASSIFIER (Dictionary-Based)
# ===========================================================================

TIER1 = [
    {"term": "ESG-linked compensation", "category": "general", "confidence": 0.95},
    {"term": "ESG-linked pay", "category": "general", "confidence": 0.95},
    {"term": "ESG modifier", "category": "structure", "confidence": 0.90},
    {"term": "ESG multiplier", "category": "structure", "confidence": 0.90},
    {"term": "sustainability metrics in compensation", "category": "general", "confidence": 0.90},
    {"term": "TRIR", "category": "social_safety", "confidence": 0.90},
    {"term": "Scope 3 emissions", "category": "environmental", "confidence": 0.85},
    {"term": "diversity goals", "category": "social_dei", "confidence": 0.85},
    {"term": "emissions reduction targets", "category": "environmental", "confidence": 0.85},
]

TIER2 = [
    {"term": "climate targets", "category": "environmental", "max_distance_words": 200},
    {"term": "safety performance", "category": "social", "max_distance_words": 200},
    {"term": "employee engagement", "category": "social", "max_distance_words": 200},
    {"term": "renewable energy", "category": "environmental", "max_distance_words": 200},
    {"term": "diversity and inclusion", "category": "social", "max_distance_words": 200},
    {"term": "board diversity", "category": "governance", "max_distance_words": 200},
    {"term": "emissions reduction", "category": "environmental", "max_distance_words": 200},
]

TIER3 = [
    {"term": "sustainability", "category": "general", "weight": 0.5},
    {"term": "environmental", "category": "general", "weight": 0.3},
    {"term": "social", "category": "general", "weight": 0.3},
    {"term": "governance", "category": "general", "weight": 0.3},
    {"term": "ESG", "category": "general", "weight": 0.4},
]

COMP_TERMS = [
    "compensation", "incentive", "bonus", "pay", "annual incentive plan",
    "long-term incentive", "LTIP", "AIP", "short-term incentive", "STIP"
]

WORD_RE = re.compile(r"\b\w[\w'-]*\b", flags=re.UNICODE)


def tokenize_words(text: str) -> List[str]:
    if not text:
        return []
    return WORD_RE.findall(text.lower())


def count_term_in_text(text: str, term: str) -> int:
    if not text or not term:
        return 0
    return len(re.findall(re.escape(term), text, flags=re.IGNORECASE))


def split_into_sentences(text: str) -> List[str]:
    if not text:
        return []
    return re.split(r'(?<=[\.\?\!])\s+', text.strip())


def find_terms_within_distance(text: str, term1: str, term2_list: List[str], max_distance: int = 200) -> List[Dict[str, Any]]:
    words = tokenize_words(text)
    if not words:
        return []
    
    def find_sequence_positions(seq_words: List[str]) -> List[int]:
        if not seq_words:
            return []
        positions = []
        L = len(seq_words)
        for i in range(len(words) - L + 1):
            if words[i:i + L] == seq_words:
                positions.append(i)
        return positions
    
    t1_positions = find_sequence_positions(tokenize_words(term1))
    matches = []
    for comp in term2_list:
        comp_positions = find_sequence_positions(tokenize_words(comp))
        for p1 in t1_positions:
            for p2 in comp_positions:
                if abs(p1 - p2) <= max_distance:
                    matches.append({
                        "esg_term": term1,
                        "comp_term": comp,
                        "distance_words": abs(p1 - p2)
                    })
    return matches


def extract_section(text: str, section_identifiers: List[str]) -> str:
    if not text:
        return ""
    
    text_lower = text.lower()
    start_pos = None
    for ident in section_identifiers:
        pos = text_lower.find(ident.lower())
        if pos != -1 and (start_pos is None or pos < start_pos):
            start_pos = pos
    
    if start_pos is None:
        return ""
    
    match = re.search(r"\n[A-Z][A-Z\s\-\.\&]{3,}\n", text[start_pos + 20:])
    end_pos = (start_pos + 20 + match.start()) if match else None
    
    if end_pos:
        return text[start_pos:end_pos].strip()
    else:
        return text[start_pos:start_pos + 20000].strip()


def identify_esg_pay(proxy_text: str, cd_and_a_section: str) -> Dict[str, Any]:
    if not cd_and_a_section:
        return {"ESG_PAY": None, "confidence": "missing_cd_and_a", "matched_terms": [], "tier": None}
    
    txt = cd_and_a_section
    tier1_matches = []
    for row in TIER1:
        term = row["term"]
        if re.search(re.escape(term), txt, flags=re.IGNORECASE):
            if "esg-linked" in term.lower() or len(find_terms_within_distance(txt, term, COMP_TERMS, 400)) > 0:
                tier1_matches.append(term)
    
    if tier1_matches:
        return {"ESG_PAY": 1, "confidence": "high", "matched_terms": tier1_matches, "tier": 1}
    
    tier2_matches = []
    for row in TIER2:
        term = row["term"]
        if re.search(re.escape(term), txt, flags=re.IGNORECASE):
            max_dist = int(row.get("max_distance_words", 200))
            if find_terms_within_distance(txt, term, COMP_TERMS, max_dist):
                tier2_matches.append(term)
    
    if len(tier2_matches) >= 1:
        return {"ESG_PAY": 1, "confidence": "medium", "matched_terms": tier2_matches, "tier": 2}
    
    return {"ESG_PAY": 0, "confidence": "none", "matched_terms": [], "tier": 3}


def calculate_esg_intensity(cd_and_a_section: Optional[str]) -> Dict[str, Any]:
    txt = cd_and_a_section or ""
    e_terms = [r["term"] for r in TIER2 if "environment" in r["category"] or r["category"] == "environmental"]
    s_terms = [r["term"] for r in TIER2 if "social" in r["category"] or r["category"] == "social"]
    g_terms = [r["term"] for r in TIER2 if "governance" in r["category"] or r["category"] == "governance"]
    
    E_count = S_count = G_count = 0
    seen_terms = set()
    
    for s in split_into_sentences(txt):
        if any(ct.lower() in s.lower() for ct in COMP_TERMS):
            for term in e_terms:
                if term.lower() in s.lower() and term not in seen_terms:
                    E_count += 1
                    seen_terms.add(term)
            for term in s_terms:
                if term.lower() in s.lower() and term not in seen_terms:
                    S_count += 1
                    seen_terms.add(term)
            for term in g_terms:
                if term.lower() in s.lower() and term not in seen_terms:
                    G_count += 1
                    seen_terms.add(term)
    
    total = E_count + S_count + G_count
    return {
        "ESG_PAY_INTENSITY": total,
        "E_count": E_count,
        "S_count": S_count,
        "G_count": G_count,
        "ESG_PAY_BREADTH": sum(1 for v in (E_count, S_count, G_count) if v > 0),
    }


def weighted_esg_score(cd_and_a_section: Optional[str], threshold: float = 2.0) -> Dict[str, Any]:
    txt = cd_and_a_section or ""
    score = 0.0
    matches: List[Dict[str, Any]] = []
    
    for row in TIER1:
        term = row["term"]
        confidence = float(row.get("confidence", 0.9))
        weight = max(1.0, confidence * 3.0)
        cnt = count_term_in_text(txt, term)
        if cnt > 0:
            score += cnt * weight
            matches.append({"term": term, "count": cnt, "weight": weight})
    
    for row in TIER2:
        term = row["term"]
        cnt = count_term_in_text(txt, term)
        if cnt > 0:
            score += cnt * 2.0
            matches.append({"term": term, "count": cnt, "weight": 2.0})
    
    for row in TIER3:
        term = row["term"]
        weight = float(row.get("weight", 0.3))
        cnt = count_term_in_text(txt, term)
        if cnt > 0:
            score += cnt * weight
            matches.append({"term": term, "count": cnt, "weight": weight})
    
    return {"ESG_PAY_SCORE": score, "matched_terms": matches, "ESG_PAY_weighted_binary": 1 if score >= threshold else 0}


def identify_ceo_specific(cd_and_a: Optional[str]) -> Dict[str, bool]:
    s = (cd_and_a or "").lower()
    ceo_indicators = ["chief executive officer", "ceo", "president and ceo"]
    neo_indicators = ["named executive officers", "neos", "senior management"]
    return {
        "applies_to_ceo": any(ind in s for ind in ceo_indicators),
        "mentions_neo": any(ind in s for ind in neo_indicators)
    }


def process_proxy_statement(firm_id: Any, year: Any, proxy_text: str) -> Dict[str, Any]:
    """Main function to analyze ESG compensation in proxy statement."""
    cd_and_a = extract_section(proxy_text, ["Compensation Discussion and Analysis", "CD&A", "Compensation Discussion & Analysis"])
    id_res = identify_esg_pay(proxy_text, cd_and_a)
    intensity = calculate_esg_intensity(cd_and_a)
    weighted = weighted_esg_score(cd_and_a)
    ceo_info = identify_ceo_specific(cd_and_a)
    
    matched_from_id = id_res.get("matched_terms", []) or []
    matched_from_weight = [m.get("term") for m in weighted.get("matched_terms", [])] if weighted.get("matched_terms") else []
    matched_terms = list(dict.fromkeys([t for t in (matched_from_id + matched_from_weight) if t]))
    
    return {
        "firm_id": firm_id,
        "year": year,
        "ESG_PAY": id_res.get("ESG_PAY"),
        "ESG_PAY_confidence": id_res.get("confidence"),
        "ESG_PAY_tier": id_res.get("tier"),
        "matched_terms": matched_terms,
        "E_metrics": intensity.get("E_count"),
        "S_metrics": intensity.get("S_count"),
        "G_metrics": intensity.get("G_count"),
        "ESG_PAY_INTENSITY": intensity.get("ESG_PAY_INTENSITY"),
        "ESG_PAY_BREADTH": intensity.get("ESG_PAY_BREADTH"),
        "ESG_PAY_SCORE": weighted.get("ESG_PAY_SCORE"),
        "ESG_PAY_weighted_binary": weighted.get("ESG_PAY_weighted_binary"),
        "cd_and_a_wordcount": len((cd_and_a or "").split()),
        "proxy_available": bool(proxy_text),
        "cd_and_a_found": bool(cd_and_a),
        "applies_to_ceo": ceo_info.get("applies_to_ceo"),
        "mentions_neo": ceo_info.get("mentions_neo"),
    }


# ===========================================================================
# DEMO / EXAMPLE
# ===========================================================================

def run_demo():
    """Run demo with example text."""
    print("="*70)
    print("ESG COMPENSATION ANALYZER - DEMO")
    print("="*70)
    
    # Example 1: With ESG linkage
    demo_text_1 = """
    Compensation Discussion and Analysis
    
    Our executive compensation program includes ESG-linked pay with an ESG modifier.
    The annual bonus plan for our CEO and named executive officers incorporates:
    - Emissions reduction targets (30% weight)
    - Diversity goals for leadership positions (20% weight)
    - Safety performance measured by TRIR (15% weight)
    
    The long-term incentive plan includes climate targets and renewable energy goals.
    """
    
    print("\nExample 1: Company WITH ESG-linked compensation")
    print("-" * 70)
    result1 = process_proxy_statement("DEMO_ESG_CO", 2024, demo_text_1)
    print(f"ESG-Linked: {'YES ✓' if result1['ESG_PAY']==1 else 'NO ✗'}")
    print(f"Confidence: {result1['ESG_PAY_confidence']}")
    print(f"Score: {result1['ESG_PAY_SCORE']:.2f}")
    print(f"Matched Terms: {', '.join(result1['matched_terms'][:5])}")
    print(f"E/S/G Metrics: {result1['E_metrics']}/{result1['S_metrics']}/{result1['G_metrics']}")
    
    # Example 2: Without ESG linkage
    demo_text_2 = """
    Compensation Discussion and Analysis
    
    Executive compensation is based on financial performance metrics including:
    - Revenue growth
    - Earnings per share (EPS)
    - Return on equity (ROE)
    - Total shareholder return (TSR)
    
    Annual bonuses are tied to achieving quarterly financial targets.
    """
    
    print("\nExample 2: Company WITHOUT ESG-linked compensation")
    print("-" * 70)
    result2 = process_proxy_statement("DEMO_NO_ESG_CO", 2024, demo_text_2)
    print(f"ESG-Linked: {'YES ✓' if result2['ESG_PAY']==1 else 'NO ✗'}")
    print(f"Confidence: {result2['ESG_PAY_confidence']}")
    print(f"Score: {result2['ESG_PAY_SCORE']:.2f}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print("\nTo analyze your own data, use:")
    print("  result = process_proxy_statement(firm_id, year, proxy_text)")
    print("\nFor SEC data integration, install: pip install edgartools")


if __name__ == "__main__":
    run_demo()
