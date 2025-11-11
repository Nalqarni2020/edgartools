#!/usr/bin/env python3
"""Quick start examples for ESG compensation classification."""

from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Example 1: Analyze a single proxy statement
def example_single_analysis():
    proxy_text = """
    Compensation Discussion and Analysis
    Our CEO and named executive officers receive compensation that includes
    ESG-linked pay with an ESG modifier. The annual bonus is tied to 
    emissions reduction targets and diversity goals measured by representation
    in leadership roles. Safety performance is tracked using TRIR metrics.
    """
    
    result = process_proxy_statement("EXAMPLE_CO", 2024, proxy_text)
    
    print("=" * 60)
    print("SINGLE PROXY STATEMENT ANALYSIS")
    print("=" * 60)
    print(f"ESG-Linked Compensation: {'YES' if result['ESG_PAY'] == 1 else 'NO'}")
    print(f"Confidence Level: {result['ESG_PAY_confidence']}")
    print(f"Classification Tier: {result['ESG_PAY_tier']}")
    print(f"\nMatched Terms: {', '.join(result['matched_terms'][:5])}")
    print(f"\nESG Metrics Breakdown:")
    print(f"  Environmental: {result['E_metrics']}")
    print(f"  Social: {result['S_metrics']}")
    print(f"  Governance: {result['G_metrics']}")
    print(f"\nIntensity Score: {result['ESG_PAY_INTENSITY']}")
    print(f"Breadth (categories): {result['ESG_PAY_BREADTH']}")
    print(f"Weighted Score: {result['ESG_PAY_SCORE']:.2f}")
    print(f"\nApplies to CEO: {result['applies_to_ceo']}")
    print(f"Mentions NEOs: {result['mentions_neo']}")
    print()


# Example 2: Integration with edgartools
def example_edgartools_integration():
    """Example showing integration with edgartools."""
    print("=" * 60)
    print("EDGARTOOLS INTEGRATION EXAMPLE")
    print("=" * 60)
    print("""
# Import both libraries
from edgar import Company
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Get a company and its proxy statements
company = Company("AAPL")
def14a_filings = company.get_filings(form="DEF 14A").latest(3)

# Process each filing
results = []
for filing in def14a_filings:
    doc = filing.primary_document
    if doc:
        proxy_text = doc.text()  # or doc.html()
        result = process_proxy_statement(
            firm_id=company.cik,
            year=filing.filing_date.year,
            proxy_text=proxy_text
        )
        results.append(result)

# Analyze trends
import pandas as pd
df = pd.DataFrame(results)
print(df[['year', 'ESG_PAY', 'ESG_PAY_confidence', 'ESG_PAY_INTENSITY']])
    """)


# Example 3: Batch processing multiple companies
def example_batch_processing():
    print("=" * 60)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 60)
    print("""
# Process multiple companies
companies = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
all_results = []

for ticker in companies:
    company = Company(ticker)
    filings = company.get_filings(form="DEF 14A").latest(1)
    
    if len(filings) > 0:
        filing = filings[0]
        doc = filing.primary_document
        if doc:
            proxy_text = doc.text()
            result = process_proxy_statement(
                firm_id=company.cik,
                year=filing.filing_date.year,
                proxy_text=proxy_text
            )
            result['ticker'] = ticker
            all_results.append(result)

# Create summary DataFrame
df = pd.DataFrame(all_results)
summary = df[['ticker', 'year', 'ESG_PAY', 'ESG_PAY_confidence', 
              'ESG_PAY_INTENSITY', 'ESG_PAY_SCORE']]
print(summary.to_string(index=False))
    """)


# Example 4: CSV batch processing
def example_csv_processing():
    print("=" * 60)
    print("CSV BATCH PROCESSING")
    print("=" * 60)
    print("""
# Create input CSV with columns: firm_id, year, proxy_text
# Then process in batch:

from esg_compensation_pipeline_all_in_one import process_csv

process_csv('input_proxies.csv', 'output_results.csv')

# Or with pandas for more control:
import pandas as pd

df = pd.read_csv('input_proxies.csv')
results = []

for _, row in df.iterrows():
    result = process_proxy_statement(
        row['firm_id'], 
        row['year'], 
        row['proxy_text']
    )
    results.append(result)

pd.DataFrame(results).to_csv('results.csv', index=False)
    """)


if __name__ == "__main__":
    example_single_analysis()
    example_edgartools_integration()
    example_batch_processing()
    example_csv_processing()
