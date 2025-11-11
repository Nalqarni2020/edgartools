#!/usr/bin/env python3
"""
SIMPLE SEC + ESG EXAMPLE
Shortest possible example of getting SEC data and analyzing ESG compensation.

REQUIRES: pip install edgartools
"""

print("Simple SEC + ESG Analysis Example")
print("="*60)

try:
    from edgar import Company
    from esg_compensation_pipeline_all_in_one import process_proxy_statement
    
    # Step 1: Get company
    print("\n1. Getting company from SEC EDGAR...")
    company = Company("AAPL")
    print(f"   ✓ {company.name}")
    
    # Step 2: Get proxy statement
    print("\n2. Fetching proxy statement (DEF 14A)...")
    filings = company.get_filings(form="DEF 14A").latest(1)
    
    if len(filings) == 0:
        print("   ✗ No proxy statements found")
        exit(1)
    
    filing = filings[0]
    print(f"   ✓ Found filing from {filing.filing_date}")
    
    # Step 3: Extract text
    print("\n3. Extracting text from proxy...")
    doc = filing.primary_document
    proxy_text = doc.text()
    print(f"   ✓ Extracted {len(proxy_text):,} characters")
    
    # Step 4: Analyze ESG compensation
    print("\n4. Analyzing ESG compensation...")
    result = process_proxy_statement(
        firm_id=company.cik,
        year=filing.filing_date.year,
        proxy_text=proxy_text
    )
    print(f"   ✓ Analysis complete")
    
    # Step 5: Show results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Company: {company.name}")
    print(f"Year: {result['year']}")
    print(f"\nESG-Linked Compensation: {'YES ✓' if result['ESG_PAY']==1 else 'NO ✗'}")
    print(f"Confidence: {result['ESG_PAY_confidence']}")
    print(f"Classification Tier: {result['ESG_PAY_tier']}")
    print(f"\nESG Score: {result['ESG_PAY_SCORE']:.2f}")
    print(f"Intensity: {result['ESG_PAY_INTENSITY']}")
    print(f"Breadth (E/S/G): {result['E_metrics']}/{result['S_metrics']}/{result['G_metrics']}")
    
    if result['matched_terms']:
        print(f"\nTop Matched Terms:")
        for i, term in enumerate(result['matched_terms'][:5], 1):
            print(f"  {i}. {term}")
    
    print(f"\nApplies to CEO: {result['applies_to_ceo']}")
    print(f"CD&A Section Found: {result['cd_and_a_found']}")
    print(f"CD&A Word Count: {result['cd_and_a_wordcount']:,}")
    
    print("\n" + "="*60)
    print("✓ SUCCESS!")
    print("="*60)
    print("\nTo analyze other companies, change 'AAPL' to any ticker:")
    print("  company = Company('MSFT')  # Microsoft")
    print("  company = Company('TSLA')  # Tesla")
    print("  company = Company('XOM')   # Exxon Mobil")

except ImportError as e:
    print("\n" + "="*60)
    print("ERROR: Missing dependency")
    print("="*60)
    print(f"\n{e}")
    print("\nPlease install required packages:")
    print("  pip install edgartools pandas")
    print("\nOr run a simpler example that doesn't need SEC data:")
    print("  python3 run_esg_example.py")
    print("  python3 COPY_THIS_SCRIPT.py")

except Exception as e:
    print("\n" + "="*60)
    print("ERROR")
    print("="*60)
    print(f"\n{e}")
    import traceback
    traceback.print_exc()
