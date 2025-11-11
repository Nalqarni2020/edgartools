"""
ESG Compensation Pipeline - Single Corrected Script

This single-file script is the corrected, Jupyter/IPython-safe, ready-to-run
version of the dictionary-based ESG-linked executive compensation classifier.

Key fixes and improvements from prior iterations:
- Uses argparse.parse_known_args() so the script can be imported or run inside Jupyter
  without ipykernel CLI noise causing SystemExit.
- Serializes list/dict fields (e.g., matched_terms) to JSON when writing CSV via
  the csv module and normalizes before saving with pandas.
- Ensures the CLI demo remains available, and provides process_proxy_statement()
  as an importable function for use inside notebooks.
- Minor robustness improvements (safe defaults, clearer names).

Usage (recommended in notebook/script):
    from esg_compensation_pipeline_all_in_one import process_proxy_statement
    result = process_proxy_statement("FIRM_ID", 2020, proxy_text)
    print(result)

CLI usage (from terminal):
    python esg_compensation_pipeline_all_in_one.py --demo
    python esg_compensation_pipeline_all_in_one.py --input proxies.csv --output results.csv

Notes:
- Input CSV (if using CLI batch) must include columns: firm_id, year, proxy_text.
- This script focuses on text logic; integrate your PDF/HTML extractor upstream
  (SEC-API, pdfminer.six, GROBID) to produce proxy_text.
"""

from typing import List, Dict, Any, Optional
import re
import csv
import json
import argparse
import random

# Optional libs
try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None

try:
    from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix  # type: ignore
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False

# ---------------------------
# Dictionaries (embedded)
# ---------------------------

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
    {"term": "climate targets", "category": "environmental", "requires_context": True, "max_distance_words": 200},
    {"term": "safety performance", "category": "social", "requires_context": True, "max_distance_words": 200},
    {"term": "employee engagement", "category": "social", "requires_context": True, "max_distance_words": 200},
    {"term": "renewable energy", "category": "environmental", "requires_context": True, "max_distance_words": 200},
    {"term": "diversity and inclusion", "category": "social", "requires_context": True, "max_distance_words": 200},
    {"term": "board diversity", "category": "governance", "requires_context": True, "max_distance_words": 200},
    {"term": "emissions reduction", "category": "environmental", "requires_context": True, "max_distance_words": 200},
    {"term": "diversity goals", "category": "social", "requires_context": True, "max_distance_words": 200},
]

TIER3 = [
    {"term": "sustainability", "category": "general", "weight": 0.5, "use_for_intensity_only": True},
    {"term": "environmental", "category": "general", "weight": 0.3, "use_for_intensity_only": True},
    {"term": "social", "category": "general", "weight": 0.3, "use_for_intensity_only": True},
    {"term": "governance", "category": "general", "weight": 0.3, "use_for_intensity_only": True},
    {"term": "ESG", "category": "general", "weight": 0.4, "use_for_intensity_only": True},
]

COMP_TERMS = [
    "compensation", "incentive", "bonus", "pay", "annual incentive plan",
    "long-term incentive", "LTIP", "AIP", "short-term incentive", "STIP"
]

GREENWASH_PATTERNS = [
    "committed to sustainability",
    "environmental stewardship",
    "sustainable business practices",
    "ESG considerations"
]

GOVERNANCE_ONLY_TERMS = [
    "board ESG oversight",
    "ESG committee",
    "sustainability committee"
]

# ---------------------------
# Text utilities
# ---------------------------

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

# ---------------------------
# Section extraction
# ---------------------------


def extract_section(text: str, section_identifiers: List[str], lookahead_identifiers: Optional[List[str]] = None) -> str:
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

    if lookahead_identifiers:
        end_pos = None
        for ident in lookahead_identifiers:
            pos = text_lower.find(ident.lower(), start_pos + 1)
            if pos != -1 and (end_pos is None or pos < end_pos):
                end_pos = pos
    else:
        match = re.search(r"\n[A-Z][A-Z\s\-\.\&]{3,}\n", text[start_pos + 20:])
        end_pos = (start_pos + 20 + match.start()) if match else None

    if end_pos:
        return text[start_pos:end_pos].strip()
    else:
        return text[start_pos:start_pos + 20000].strip()

# ---------------------------
# Classification logic
# ---------------------------


def is_near_comp_term(text: str, esg_term: str, comp_terms: Optional[List[str]] = None, max_distance: int = 300) -> bool:
    comp_terms = comp_terms or COMP_TERMS
    matches = find_terms_within_distance(text, esg_term, comp_terms, max_distance)
    return len(matches) > 0


def identify_esg_pay(proxy_text: str, cd_and_a_section: str) -> Dict[str, Any]:
    if not cd_and_a_section:
        return {"ESG_PAY": None, "confidence": "missing_cd_and_a", "matched_terms": [], "tier": None}

    txt = cd_and_a_section
    tier1_matches = []
    for row in TIER1:
        term = row["term"]
        if re.search(re.escape(term), txt, flags=re.IGNORECASE):
            # require proximity unless explicit phrase
            if "esg-linked" in term.lower() or is_near_comp_term(txt, term, COMP_TERMS, max_distance=400):
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

    supplementary_matches = [row["term"] for row in TIER3 if re.search(re.escape(row["term"]), txt, flags=re.IGNORECASE)]
    total = E_count + S_count + G_count
    return {
        "ESG_PAY_INTENSITY": total,
        "E_count": E_count,
        "S_count": S_count,
        "G_count": G_count,
        "ESG_PAY_BREADTH": sum(1 for v in (E_count, S_count, G_count) if v > 0),
        "supplementary_matches": supplementary_matches
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

# ---------------------------
# Edge case helpers
# ---------------------------


def is_greenwashing(sentence: str) -> bool:
    s = sentence.lower()
    has_generic = any(pat in s for pat in GREENWASH_PATTERNS)
    has_specific = any(row["term"].lower() in s for row in TIER1)
    return has_generic and not has_specific


def distinguish_governance_vs_compensation(text: str) -> str:
    s = (text or "").lower()
    if any(term in s for term in GOVERNANCE_ONLY_TERMS) and not any(ct in s for ct in COMP_TERMS):
        return "governance_not_compensation"
    return "potential_esg_compensation"


def identify_ceo_specific(cd_and_a: Optional[str]) -> Dict[str, bool]:
    s = (cd_and_a or "").lower()
    ceo_indicators = ["chief executive officer", "ceo", "president and ceo"]
    neo_indicators = ["named executive officers", "neos", "senior management"]
    return {
        "applies_to_ceo": any(ind in s for ind in ceo_indicators),
        "mentions_neo": any(ind in s for ind in neo_indicators)
    }

# ---------------------------
# Main processing entrypoint
# ---------------------------


def process_proxy_statement(firm_id: Any, year: Any, proxy_text: str) -> Dict[str, Any]:
    cd_and_a = extract_section(proxy_text, ["Compensation Discussion and Analysis", "CD&A", "Compensation Discussion & Analysis"])
    id_res = identify_esg_pay(proxy_text, cd_and_a)
    intensity = calculate_esg_intensity(cd_and_a)
    weighted = weighted_esg_score(cd_and_a)
    ceo_info = identify_ceo_specific(cd_and_a)
    gov_vs_comp = distinguish_governance_vs_compensation(cd_and_a)

    # merge matched terms into a deduplicated list (strings only)
    matched_from_id = id_res.get("matched_terms", []) or []
    matched_from_weight = [m.get("term") for m in weighted.get("matched_terms", [])] if weighted.get("matched_terms") else []
    matched_terms = list(dict.fromkeys([t for t in (matched_from_id + matched_from_weight) if t]))

    out = {
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
        "governance_vs_compensation_flag": gov_vs_comp
    }
    return out

# ---------------------------
# Validation helpers
# ---------------------------


def stratified_sample(df, label_col: str = "ESG_PAY", n: int = 100, strata_cols=None, random_state: int = 42):
    if pd is None:
        sample = random.sample(list(df), min(n, len(df)))
        return sample

    if strata_cols is None:
        if label_col in df.columns:
            pos = df[df[label_col] == 1]
            neg = df[df[label_col] == 0]
            n_pos = n // 2
            n_neg = n - n_pos
            sample = pd.concat([
                pos.sample(n=min(n_pos, len(pos)), random_state=random_state) if len(pos) > 0 else pos,
                neg.sample(n=min(n_neg, len(neg)), random_state=random_state) if len(neg) > 0 else neg
            ])
            return sample.sample(frac=1, random_state=random_state)
        else:
            return df.sample(n=min(n, len(df)), random_state=random_state)
    else:
        grouped = df.groupby(strata_cols)
        samples = []
        per_group = max(1, n // max(1, len(grouped)))
        for _, g in grouped:
            samples.append(g.sample(n=min(per_group, len(g)), random_state=random_state))
        return pd.concat(samples).sample(n=min(n, len(df)), random_state=random_state)


def compute_validation_metrics(manual_labels: List[int], auto_labels: List[int]) -> Dict[str, Any]:
    if len(manual_labels) != len(auto_labels):
        raise ValueError("Labels must have same length")
    if _SKLEARN_AVAILABLE:
        precision = precision_score(manual_labels, auto_labels)
        recall = recall_score(manual_labels, auto_labels)
        f1 = f1_score(manual_labels, auto_labels)
        tn, fp, fn, tp = confusion_matrix(manual_labels, auto_labels).ravel()
    else:
        tp = sum(1 for m, a in zip(manual_labels, auto_labels) if m == 1 and a == 1)
        tn = sum(1 for m, a in zip(manual_labels, auto_labels) if m == 0 and a == 0)
        fp = sum(1 for m, a in zip(manual_labels, auto_labels) if m == 0 and a == 1)
        fn = sum(1 for m, a in zip(manual_labels, auto_labels) if m == 1 and a == 0)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn)}

# ---------------------------
# Batch CSV processing
# ---------------------------


def process_csv(input_path: str, output_path: str, chunk_size: int = 1000):
    if pd is None:
        with open(input_path, newline="", encoding="utf-8") as f_in, open(output_path, "w", newline="", encoding="utf-8") as f_out:
            reader = csv.DictReader(f_in)
            writer = None
            for row in reader:
                res = process_proxy_statement(row.get("firm_id"), row.get("year"), row.get("proxy_text", ""))
                # serialize lists/dicts to JSON for CSV-safe output
                serial = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in res.items()}
                if writer is None:
                    fieldnames = list(serial.keys())
                    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerow(serial)
        return

    # pandas branch
    results = []
    for chunk in pd.read_csv(input_path, chunksize=chunk_size, iterator=True, encoding="utf-8"):
        for _, row in chunk.iterrows():
            res = process_proxy_statement(row.get("firm_id"), row.get("year"), row.get("proxy_text", ""))
            results.append(res)
    out_df = pd.DataFrame(results)
    # ensure matched_terms (and any lists) are serialized
    if 'matched_terms' in out_df.columns:
        out_df['matched_terms'] = out_df['matched_terms'].apply(lambda x: json.dumps(x) if not pd.isna(x) else json.dumps([]))
    out_df.to_csv(output_path, index=False, encoding="utf-8")

# ---------------------------
# CLI
# ---------------------------


def main_cli():
    parser = argparse.ArgumentParser(description="ESG compensation dictionary pipeline - single script")
    parser.add_argument("--input", "-i", help="Input CSV path (firm_id, year, proxy_text)", required=False)
    parser.add_argument("--output", "-o", help="Output CSV path", required=False)
    parser.add_argument("--demo", action="store_true", help="Run demo example")
    args, unknown = parser.parse_known_args()  # safe for notebooks

    if args.demo:
        demo_text = """
        Compensation Discussion and Analysis
        Our annual incentive plan includes sustainability metrics. The CEO's annual bonus
        is partly tied to emissions reduction targets and diversity goals. The LTIP uses an ESG modifier.
        """
        print("Demo input text:\n", demo_text)
        res = process_proxy_statement("DEMO_CO", 2024, demo_text)
        print(json.dumps(res, indent=2))
        return

    if args.input and args.output:
        process_csv(args.input, args.output)
        print(f"Wrote results to {args.output}")
        return

    parser.print_help()


if __name__ == "__main__":
    main_cli()
