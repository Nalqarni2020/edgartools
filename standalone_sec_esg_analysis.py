#!/usr/bin/env python3
"""
STANDALONE SEC + ESG ANALYSIS
Everything in one file - no import issues!

REQUIRES: pip install edgartools pandas
RUN: python3 standalone_sec_esg_analysis.py
"""

import sys
import os

# Add current directory to Python path (fixes import issues)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now try to import
try:
    from esg_compensation_pipeline_all_in_one import process_proxy_statement
    print("✓ ESG classifier loaded successfully\n")
except ImportError as e:
    print(f"ERROR: {e}\n")
    print("SOLUTION: Run this from the /workspace directory:")
    print("  cd /workspace")
    print("  python3 standalone_sec_esg_analysis.py")
    print("\nOr copy esg_compensation_pipeline_all_in_one.py to the same folder.\n")
    sys.exit(1)

try:
    from edgar import Company
    print("✓ edgartools loaded successfully\n")
except ImportError:
    print("ERROR: edgartools not installed")
    print("\nSOLUTION: Install it with:")
    print("  pip install edgartools pandas")
    print("\nThen run this script again.\n")
    sys.exit(1)

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_company_from_sec(ticker: str, num_years: int = 1):
    """
    Get proxy statement from SEC and analyze ESG compensation.
    
    Args:
        ticker: Stock ticker (e.g., 'AAPL', 'MSFT')
        num_years: Number of recent proxy statements to analyze
    
    Returns:
        List of results
    """
    print("="*70)
    print(f"ANALYZING: {ticker}")
    print("="*70)
    
    try:
        # Step 1: Get company from SEC
        print("\n1. Connecting to SEC EDGAR...")
        company = Company(ticker)
        print(f"   ✓ Found: {company.name}")
        print(f"   CIK: {company.cik}")
        
        # Step 2: Get proxy statements
        print(f"\n2. Fetching proxy statements (DEF 14A)...")
        filings = company.get_filings(form="DEF 14A").latest(num_years)
        
        if len(filings) == 0:
            print(f"   ✗ No proxy statements found for {ticker}")
            return []
        
        print(f"   ✓ Found {len(filings)} proxy statement(s)")
        
        # Step 3: Process each filing
        results = []
        for i, filing in enumerate(filings, 1):
            print(f"\n--- Processing Filing {i}/{len(filings)} ---")
            print(f"Date: {filing.filing_date}")
            print(f"Accession: {filing.accession_number}")
            
            # Extract text
            print("Extracting text...")
            doc = filing.primary_document
            if not doc:
                print("⚠ Could not get document")
                continue
            
            try:
                proxy_text = doc.text()
            except:
                try:
                    proxy_text = doc.html()
                except:
                    print("⚠ Could not extract text")
                    continue
            
            print(f"✓ Extracted {len(proxy_text):,} characters")
            
            # Analyze ESG compensation
            print("Analyzing ESG compensation...")
            result = process_proxy_statement(
                firm_id=company.cik,
                year=filing.filing_date.year,
                proxy_text=proxy_text
            )
            
            # Add metadata
            result['ticker'] = ticker
            result['company_name'] = company.name
            result['filing_date'] = str(filing.filing_date)
            
            results.append(result)
            
            # Display quick summary
            esg_status = "✓ YES" if result['ESG_PAY'] == 1 else "✗ NO"
            print(f"ESG-Linked: {esg_status} (Confidence: {result['ESG_PAY_confidence']})")
            print(f"Score: {result['ESG_PAY_SCORE']:.2f}")
        
        return results
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []


def display_results(results):
    """Display results in a nice format."""
    if not results:
        print("\nNo results to display.")
        return
    
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for result in results:
        print(f"\nCompany: {result.get('company_name', 'N/A')}")
        print(f"Ticker: {result.get('ticker', 'N/A')}")
        print(f"Year: {result['year']}")
        print(f"Filing Date: {result.get('filing_date', 'N/A')}")
        print("-" * 70)
        print(f"ESG-Linked Compensation: {'YES ✓' if result['ESG_PAY']==1 else 'NO ✗'}")
        print(f"Confidence Level: {result['ESG_PAY_confidence']}")
        print(f"Classification Tier: {result['ESG_PAY_tier']}")
        print(f"\nScoring:")
        print(f"  ESG Score: {result['ESG_PAY_SCORE']:.2f}")
        print(f"  Intensity: {result['ESG_PAY_INTENSITY']}")
        print(f"  Breadth: {result['ESG_PAY_BREADTH']} categories")
        print(f"\nE/S/G Metrics:")
        print(f"  Environmental: {result['E_metrics']}")
        print(f"  Social: {result['S_metrics']}")
        print(f"  Governance: {result['G_metrics']}")
        
        if result['matched_terms']:
            print(f"\nMatched Terms ({len(result['matched_terms'])} total):")
            for term in result['matched_terms'][:8]:
                print(f"  • {term}")
        
        print(f"\nAdditional Info:")
        print(f"  Applies to CEO: {result['applies_to_ceo']}")
        print(f"  Mentions NEOs: {result['mentions_neo']}")
        print(f"  CD&A Word Count: {result['cd_and_a_wordcount']:,}")
        print(f"  CD&A Found: {result['cd_and_a_found']}")


def analyze_multiple_companies(tickers: list):
    """Analyze multiple companies and create summary."""
    print("\n" + "="*70)
    print("MULTI-COMPANY ANALYSIS")
    print("="*70)
    print(f"Companies to analyze: {', '.join(tickers)}\n")
    
    all_results = []
    
    for ticker in tickers:
        results = analyze_company_from_sec(ticker, num_years=1)
        all_results.extend(results)
        print()  # Blank line between companies
    
    if not all_results:
        print("No results collected.")
        return
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Ticker':<8} {'Year':<6} {'ESG':<5} {'Confidence':<12} {'Score':<8} {'E/S/G'}")
    print("-" * 70)
    
    for r in all_results:
        esg_symbol = "✓" if r['ESG_PAY'] == 1 else "✗"
        esg_metrics = f"{r['E_metrics']}/{r['S_metrics']}/{r['G_metrics']}"
        print(f"{r['ticker']:<8} {r['year']:<6} {esg_symbol:<5} "
              f"{r['ESG_PAY_confidence']:<12} {r['ESG_PAY_SCORE']:<8.2f} {esg_metrics}")
    
    # Statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    total = len(all_results)
    esg_linked = sum(1 for r in all_results if r['ESG_PAY'] == 1)
    avg_score = sum(r['ESG_PAY_SCORE'] for r in all_results) / total if total > 0 else 0
    
    print(f"Total companies analyzed: {total}")
    print(f"ESG-linked compensation: {esg_linked} ({esg_linked/total*100:.1f}%)")
    print(f"Average ESG Score: {avg_score:.2f}")
    
    return all_results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          STANDALONE SEC + ESG COMPENSATION ANALYSIS                  ║
║              Get data from SEC → Analyze ESG pay                     ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Example 1: Single company
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Company Analysis")
    print("="*70)
    
    results = analyze_company_from_sec("AAPL", num_years=2)
    display_results(results)
    
    # Example 2: Multiple companies
    print("\n\n" + "="*70)
    print("EXAMPLE 2: Multiple Companies Comparison")
    print("="*70)
    
    tech_companies = ["AAPL", "MSFT", "GOOGL"]
    all_results = analyze_multiple_companies(tech_companies)
    
    # Save to CSV (optional)
    try:
        import pandas as pd
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Prepare for CSV
            import json
            if 'matched_terms' in df.columns:
                df['matched_terms'] = df['matched_terms'].apply(json.dumps)
            
            filename = "sec_esg_results.csv"
            df.to_csv(filename, index=False)
            print(f"\n✓ Results saved to: {filename}")
    except ImportError:
        print("\nNote: Install pandas to save results to CSV")
        print("  pip install pandas")
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nTo analyze different companies, edit the tickers in this script:")
    print("  tech_companies = ['AAPL', 'MSFT', 'GOOGL']")
    print("\nOr create your own analysis:")
    print("  results = analyze_company_from_sec('YOUR_TICKER', num_years=3)")
