"""Local test file for ESG compensation classifier - Ready to run in PyCharm."""

from esg_compensation_pipeline_all_in_one import process_proxy_statement

def test_basic_example():
    """Test basic ESG classification."""
    proxy_text = """
    Compensation Discussion and Analysis
    Our executive compensation includes ESG-linked pay with an ESG modifier.
    The annual bonus is tied to emissions reduction targets and diversity goals.
    Safety performance is measured using TRIR metrics.
    """
    
    result = process_proxy_statement("DEMO_FIRM", 2024, proxy_text)
    
    print("=" * 60)
    print("ESG COMPENSATION ANALYSIS RESULTS")
    print("=" * 60)
    print(f"ESG-Linked: {result['ESG_PAY']}")
    print(f"Confidence: {result['ESG_PAY_confidence']}")
    print(f"Tier: {result['ESG_PAY_tier']}")
    print(f"\nMatched Terms:")
    for term in result['matched_terms']:
        print(f"  - {term}")
    print(f"\nMetrics:")
    print(f"  Environmental: {result['E_metrics']}")
    print(f"  Social: {result['S_metrics']}")
    print(f"  Governance: {result['G_metrics']}")
    print(f"  Intensity: {result['ESG_PAY_INTENSITY']}")
    print(f"  Score: {result['ESG_PAY_SCORE']:.2f}")
    print(f"\nApplies to CEO: {result['applies_to_ceo']}")
    print(f"Mentions NEOs: {result['mentions_neo']}")


def test_no_esg_example():
    """Test case with no ESG linkage."""
    proxy_text = """
    Compensation Discussion and Analysis
    Executive compensation is based on financial performance metrics including
    revenue growth, earnings per share, and return on equity. Bonuses are
    tied to achieving quarterly targets.
    """
    
    result = process_proxy_statement("NON_ESG_FIRM", 2024, proxy_text)
    
    print("\n" + "=" * 60)
    print("NO ESG COMPENSATION EXAMPLE")
    print("=" * 60)
    print(f"ESG-Linked: {result['ESG_PAY']}")
    print(f"Confidence: {result['ESG_PAY_confidence']}")
    print(f"Score: {result['ESG_PAY_SCORE']:.2f}")


def test_with_edgartools():
    """Test integration with edgartools."""
    try:
        from edgar import Company
        
        print("\n" + "=" * 60)
        print("REAL-WORLD EXAMPLE WITH EDGARTOOLS")
        print("=" * 60)
        
        # Get Apple's latest proxy statement
        company = Company("AAPL")
        print(f"\nAnalyzing: {company.name} (CIK: {company.cik})")
        
        filings = company.get_filings(form="DEF 14A").latest(1)
        
        if len(filings) > 0:
            filing = filings[0]
            print(f"Filing date: {filing.filing_date}")
            print(f"Accession: {filing.accession_number}")
            
            doc = filing.primary_document
            if doc:
                # Extract text
                print("Extracting proxy text...")
                try:
                    proxy_text = doc.text()
                except:
                    try:
                        proxy_text = doc.html()
                    except:
                        proxy_text = str(doc)
                
                print(f"Extracted {len(proxy_text):,} characters")
                
                # Analyze
                print("Analyzing ESG compensation...")
                result = process_proxy_statement(
                    company.cik,
                    filing.filing_date.year,
                    proxy_text
                )
                
                print(f"\nYear: {result['year']}")
                print(f"ESG-Linked: {result['ESG_PAY']}")
                print(f"Confidence: {result['ESG_PAY_confidence']}")
                print(f"Tier: {result['ESG_PAY_tier']}")
                print(f"Intensity: {result['ESG_PAY_INTENSITY']}")
                print(f"Score: {result['ESG_PAY_SCORE']:.2f}")
                
                if result['matched_terms']:
                    print(f"\nTop Matched Terms:")
                    for term in result['matched_terms'][:5]:
                        print(f"  - {term}")
                
                print(f"\nCD&A Word Count: {result['cd_and_a_wordcount']:,}")
                print(f"CD&A Found: {result['cd_and_a_found']}")
            else:
                print("Could not extract document")
        else:
            print("No DEF 14A filings found")
    
    except ImportError:
        print("\nNote: edgartools not available. Install with: pip install edgartools")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_companies():
    """Test multiple companies comparison."""
    try:
        from edgar import Company
        import pandas as pd
        
        print("\n" + "=" * 60)
        print("MULTI-COMPANY COMPARISON")
        print("=" * 60)
        
        companies = ["AAPL", "MSFT", "GOOGL"]
        results = []
        
        for ticker in companies:
            try:
                company = Company(ticker)
                filings = company.get_filings(form="DEF 14A").latest(1)
                
                if len(filings) > 0:
                    filing = filings[0]
                    doc = filing.primary_document
                    
                    if doc:
                        try:
                            proxy_text = doc.text()
                        except:
                            try:
                                proxy_text = doc.html()
                            except:
                                continue
                        
                        result = process_proxy_statement(
                            company.cik,
                            filing.filing_date.year,
                            proxy_text
                        )
                        result['ticker'] = ticker
                        result['company_name'] = company.name
                        results.append(result)
                        print(f"✓ Processed {ticker}")
            except Exception as e:
                print(f"✗ Error with {ticker}: {e}")
        
        if results:
            df = pd.DataFrame(results)
            print("\nComparison Results:")
            print(df[['ticker', 'year', 'ESG_PAY', 'ESG_PAY_confidence', 
                      'ESG_PAY_INTENSITY', 'ESG_PAY_SCORE']].to_string(index=False))
        
    except ImportError as e:
        print(f"\nNote: Missing dependency - {e}")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    print("ESG COMPENSATION CLASSIFIER - PYCHARM TEST")
    print("=" * 60)
    
    # Run all tests
    test_basic_example()
    test_no_esg_example()
    test_with_edgartools()
    test_multiple_companies()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Modify the proxy_text in test_basic_example() to test your own data")
    print("2. Change company tickers in test_multiple_companies()")
    print("3. See PYCHARM_USAGE_GUIDE.md for more usage patterns")
