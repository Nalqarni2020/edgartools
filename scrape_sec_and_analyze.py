#!/usr/bin/env python3
"""
SEC DATA EXTRACTION + ESG ANALYSIS
Get proxy statements from SEC EDGAR and analyze ESG compensation.

No web scraping needed - uses edgartools API!
"""

from edgar import Company
from esg_compensation_pipeline_all_in_one import process_proxy_statement
import pandas as pd
from datetime import datetime

def analyze_single_company(ticker: str, num_years: int = 3):
    """
    Get proxy statements from SEC and analyze ESG compensation.
    
    Args:
        ticker: Stock ticker (e.g., 'AAPL', 'MSFT')
        num_years: Number of recent years to analyze
    """
    print(f"\n{'='*70}")
    print(f"ANALYZING: {ticker}")
    print(f"{'='*70}")
    
    try:
        # Get company from SEC EDGAR
        company = Company(ticker)
        print(f"Company: {company.name}")
        print(f"CIK: {company.cik}")
        print(f"Industry: {company.industry if hasattr(company, 'industry') else 'N/A'}")
        
        # Get proxy statements (DEF 14A filings)
        print(f"\nFetching last {num_years} proxy statements from SEC EDGAR...")
        filings = company.get_filings(form="DEF 14A").latest(num_years)
        
        if len(filings) == 0:
            print("❌ No DEF 14A filings found")
            return []
        
        print(f"✓ Found {len(filings)} proxy statements")
        
        # Analyze each filing
        results = []
        for i, filing in enumerate(filings, 1):
            print(f"\n--- Filing {i}/{len(filings)} ---")
            print(f"Date: {filing.filing_date}")
            print(f"Accession: {filing.accession_number}")
            
            # Get primary document
            doc = filing.primary_document
            if not doc:
                print("⚠ Could not get primary document")
                continue
            
            # Extract text from document
            print("Extracting text from proxy statement...")
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
            result['filing_date'] = filing.filing_date
            result['accession_number'] = filing.accession_number
            
            results.append(result)
            
            # Display result
            esg_status = "✓ YES" if result['ESG_PAY'] == 1 else "✗ NO"
            print(f"ESG-Linked Pay: {esg_status} ({result['ESG_PAY_confidence']})")
            print(f"Score: {result['ESG_PAY_SCORE']:.2f}")
            if result['matched_terms']:
                print(f"Top Terms: {', '.join(result['matched_terms'][:3])}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def analyze_multiple_companies(tickers: list, num_years: int = 1):
    """
    Analyze ESG compensation for multiple companies.
    
    Args:
        tickers: List of stock tickers
        num_years: Number of years per company
    """
    print(f"\n{'='*70}")
    print(f"MULTI-COMPANY ESG COMPENSATION ANALYSIS")
    print(f"{'='*70}")
    print(f"Companies: {', '.join(tickers)}")
    print(f"Years per company: {num_years}")
    
    all_results = []
    
    for ticker in tickers:
        results = analyze_single_company(ticker, num_years)
        all_results.extend(results)
    
    if not all_results:
        print("\n❌ No results to display")
        return None
    
    # Create summary DataFrame
    df = pd.DataFrame(all_results)
    
    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    
    summary_cols = ['ticker', 'year', 'ESG_PAY', 'ESG_PAY_confidence', 
                    'ESG_PAY_SCORE', 'ESG_PAY_INTENSITY', 'E_metrics', 
                    'S_metrics', 'G_metrics']
    
    print(df[summary_cols].to_string(index=False))
    
    return df


def analyze_industry(tickers: list, industry_name: str):
    """
    Analyze ESG compensation trends across an industry.
    
    Args:
        tickers: List of company tickers in the industry
        industry_name: Name of the industry
    """
    print(f"\n{'='*70}")
    print(f"INDUSTRY ANALYSIS: {industry_name}")
    print(f"{'='*70}")
    
    df = analyze_multiple_companies(tickers, num_years=1)
    
    if df is not None and len(df) > 0:
        print(f"\n{'='*70}")
        print("INDUSTRY STATISTICS")
        print(f"{'='*70}")
        
        esg_linked = df['ESG_PAY'].sum()
        total = len(df)
        pct = (esg_linked / total * 100) if total > 0 else 0
        
        print(f"Companies analyzed: {total}")
        print(f"ESG-linked compensation: {esg_linked} ({pct:.1f}%)")
        print(f"Average ESG Score: {df['ESG_PAY_SCORE'].mean():.2f}")
        print(f"Average Intensity: {df['ESG_PAY_INTENSITY'].mean():.1f}")
        
        # Breakdown by confidence
        print("\nBy Confidence Level:")
        for conf in ['high', 'medium', 'none']:
            count = (df['ESG_PAY_confidence'] == conf).sum()
            print(f"  {conf.capitalize()}: {count}")
    
    return df


def save_results_to_csv(df: pd.DataFrame, filename: str = "esg_results.csv"):
    """Save results to CSV file."""
    import json
    
    # Prepare for CSV (serialize lists)
    df_export = df.copy()
    if 'matched_terms' in df_export.columns:
        df_export['matched_terms'] = df_export['matched_terms'].apply(json.dumps)
    if 'filing_date' in df_export.columns:
        df_export['filing_date'] = df_export['filing_date'].astype(str)
    
    df_export.to_csv(filename, index=False)
    print(f"\n✓ Results saved to: {filename}")


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          SEC DATA EXTRACTION + ESG COMPENSATION ANALYSIS             ║
║                     Using edgartools + ESG Classifier                 ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # EXAMPLE 1: Single company analysis
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Company (3 years)")
    print("="*70)
    results = analyze_single_company("AAPL", num_years=3)
    
    # EXAMPLE 2: Multiple companies comparison
    print("\n" + "="*70)
    print("EXAMPLE 2: Tech Companies Comparison")
    print("="*70)
    tech_companies = ["AAPL", "MSFT", "GOOGL"]
    df_tech = analyze_multiple_companies(tech_companies, num_years=1)
    
    # EXAMPLE 3: Industry analysis
    print("\n" + "="*70)
    print("EXAMPLE 3: Industry Analysis")
    print("="*70)
    energy_companies = ["XOM", "CVX", "COP"]
    df_energy = analyze_industry(energy_companies, "Energy")
    
    # Save results
    if df_tech is not None:
        save_results_to_csv(df_tech, "tech_esg_results.csv")
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nModify this script to:")
    print("  • Change company tickers")
    print("  • Adjust number of years")
    print("  • Analyze different industries")
    print("  • Export results to CSV")
    print("\nAll data comes from SEC EDGAR - no web scraping needed!")
