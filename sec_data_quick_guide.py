#!/usr/bin/env python3
"""
QUICK GUIDE: Getting SEC Data with edgartools

This shows the basics of accessing SEC EDGAR data.
No API keys or web scraping required!
"""

from edgar import Company, get_filings
from edgar.company_reports import TenK, EightK

print("""
╔══════════════════════════════════════════════════════════════════════╗
║               SEC EDGAR DATA ACCESS - QUICK GUIDE                    ║
║                     Using edgartools library                          ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# ==============================================================================
# 1. GET COMPANY INFORMATION
# ==============================================================================
print("\n" + "="*70)
print("1. GETTING COMPANY INFORMATION")
print("="*70)

# By ticker
company = Company("AAPL")
print(f"Company Name: {company.name}")
print(f"CIK: {company.cik}")
print(f"SIC: {company.sic}")
print(f"State: {company.state_of_incorporation}")
print(f"Fiscal Year End: {company.fiscal_year_end}")

# By company name
company2 = Company("Microsoft")
print(f"\nFound: {company2.name} (ticker: MSFT)")

# ==============================================================================
# 2. GET SPECIFIC FILINGS
# ==============================================================================
print("\n" + "="*70)
print("2. GETTING FILINGS")
print("="*70)

# Get proxy statements (DEF 14A)
proxy_filings = company.get_filings(form="DEF 14A").latest(3)
print(f"\nProxy Statements (DEF 14A): {len(proxy_filings)} found")
for filing in proxy_filings:
    print(f"  • {filing.filing_date}: {filing.accession_number}")

# Get 10-K annual reports
annual_reports = company.get_filings(form="10-K").latest(2)
print(f"\n10-K Annual Reports: {len(annual_reports)} found")
for filing in annual_reports:
    print(f"  • {filing.filing_date}: {filing.accession_number}")

# Get 8-K current reports
current_reports = company.get_filings(form="8-K").latest(5)
print(f"\n8-K Current Reports: {len(current_reports)} found")

# ==============================================================================
# 3. EXTRACT DOCUMENT TEXT
# ==============================================================================
print("\n" + "="*70)
print("3. EXTRACTING DOCUMENT TEXT")
print("="*70)

if len(proxy_filings) > 0:
    latest_proxy = proxy_filings[0]
    print(f"\nExtracting from: {latest_proxy.filing_date}")
    
    # Get primary document
    doc = latest_proxy.primary_document
    
    if doc:
        # Method 1: Plain text
        text = doc.text()
        print(f"✓ Text extracted: {len(text):,} characters")
        print(f"First 200 chars: {text[:200]}...")
        
        # Method 2: HTML (preserves formatting)
        # html = doc.html()
        
        # Method 3: Get specific sections
        # For 10-K, you can get specific items
        # tenkobj = TenK(annual_reports[0])
        # mda = tenkobj.mda  # Management Discussion & Analysis

# ==============================================================================
# 4. SEARCH FILINGS
# ==============================================================================
print("\n" + "="*70)
print("4. SEARCHING FILINGS")
print("="*70)

# Search by date range
from datetime import datetime
recent_filings = company.get_filings(
    form="8-K",
    filing_date="2023-01-01:2023-12-31"
).latest(10)
print(f"\n8-Ks in 2023: {len(recent_filings)}")

# Get all filing types
all_filings = company.get_filings().latest(10)
print(f"\nLast 10 filings of any type:")
for filing in all_filings:
    print(f"  • {filing.form:10s} {filing.filing_date}")

# ==============================================================================
# 5. BATCH PROCESSING MULTIPLE COMPANIES
# ==============================================================================
print("\n" + "="*70)
print("5. BATCH PROCESSING")
print("="*70)

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
print(f"\nProcessing {len(tickers)} companies...\n")

for ticker in tickers:
    try:
        comp = Company(ticker)
        proxies = comp.get_filings(form="DEF 14A").latest(1)
        
        if len(proxies) > 0:
            print(f"✓ {ticker:6s} - {comp.name[:30]:30s} - Latest proxy: {proxies[0].filing_date}")
        else:
            print(f"✗ {ticker:6s} - No proxy statements found")
    except Exception as e:
        print(f"✗ {ticker:6s} - Error: {e}")

# ==============================================================================
# 6. AVAILABLE FILING TYPES
# ==============================================================================
print("\n" + "="*70)
print("6. COMMON SEC FILING TYPES")
print("="*70)

filing_types = {
    "DEF 14A": "Proxy Statement (Executive compensation details)",
    "10-K": "Annual Report",
    "10-Q": "Quarterly Report",
    "8-K": "Current Report (major events)",
    "S-1": "Registration Statement (IPOs)",
    "13F-HR": "Institutional Investment Manager Holdings",
    "Form 3/4/5": "Insider Trading",
    "SC 13D/G": "Beneficial Ownership",
}

print("\nYou can get any of these:")
for form, description in filing_types.items():
    print(f"  {form:12s} - {description}")

# ==============================================================================
# 7. COMPLETE EXAMPLE: PROXY STATEMENT ANALYSIS
# ==============================================================================
print("\n" + "="*70)
print("7. COMPLETE EXAMPLE: EXTRACT & ANALYZE PROXY")
print("="*70)

def get_proxy_statement(ticker: str):
    """Get latest proxy statement text."""
    company = Company(ticker)
    filings = company.get_filings(form="DEF 14A").latest(1)
    
    if len(filings) > 0:
        filing = filings[0]
        doc = filing.primary_document
        if doc:
            return {
                'company': company.name,
                'ticker': ticker,
                'date': filing.filing_date,
                'text': doc.text(),
                'url': filing.homepage_url
            }
    return None

# Example usage
print("\nFetching Apple's latest proxy statement...")
proxy_data = get_proxy_statement("AAPL")

if proxy_data:
    print(f"✓ Company: {proxy_data['company']}")
    print(f"✓ Date: {proxy_data['date']}")
    print(f"✓ Text length: {len(proxy_data['text']):,} characters")
    print(f"✓ URL: {proxy_data['url']}")
    print(f"\nFirst 300 characters:")
    print(proxy_data['text'][:300] + "...")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "="*70)
print("SUMMARY: KEY FUNCTIONS")
print("="*70)

print("""
1. Get company:
   company = Company("AAPL")

2. Get filings:
   filings = company.get_filings(form="DEF 14A").latest(5)

3. Extract text:
   doc = filing.primary_document
   text = doc.text()

4. Process multiple companies:
   for ticker in tickers:
       company = Company(ticker)
       # ... process each

5. No API keys needed - uses SEC's public EDGAR system!
""")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print("""
• Run scrape_sec_and_analyze.py to combine SEC data + ESG analysis
• Modify tickers and date ranges for your research
• Export results to CSV for further analysis
• See SEC EDGAR directly: https://www.sec.gov/edgar/
""")
