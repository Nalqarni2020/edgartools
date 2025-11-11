# 🌐 SEC Data "Scraping" Guide

## TL;DR: You Don't Need to Scrape! 

**edgartools** library already does it for you! ✨

```bash
# Install
pip install edgartools

# Get any company's proxy statement from SEC
python3 simple_sec_example.py
```

---

## 📥 Installation (One Command)

```bash
pip install edgartools pandas
```

That's it! No API keys, no authentication, no web scraping libraries needed.

---

## 🚀 Simplest Example (30 seconds)

**File**: `simple_sec_example.py`

```python
from edgar import Company
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Get Apple from SEC
company = Company("AAPL")

# Get latest proxy statement
filing = company.get_filings(form="DEF 14A").latest(1)[0]
proxy_text = filing.primary_document.text()

# Analyze ESG compensation
result = process_proxy_statement(company.cik, 2024, proxy_text)

print(f"ESG-Linked: {result['ESG_PAY']}")
print(f"Score: {result['ESG_PAY_SCORE']}")
```

**Run it**:
```bash
python3 simple_sec_example.py
```

---

## 📊 What You Can Get from SEC

### Proxy Statements (DEF 14A) - Executive Compensation
```python
company = Company("AAPL")
proxies = company.get_filings(form="DEF 14A").latest(5)

for proxy in proxies:
    text = proxy.primary_document.text()
    # Analyze compensation details
```

### Annual Reports (10-K) - Full Financials
```python
annual_reports = company.get_filings(form="10-K").latest(3)
```

### Quarterly Reports (10-Q)
```python
quarterly = company.get_filings(form="10-Q").latest(8)
```

### Current Reports (8-K) - Major Events
```python
events = company.get_filings(form="8-K").latest(20)
```

### Insider Trading (Forms 3, 4, 5)
```python
insider = company.get_filings(form="4").latest(50)
```

---

## 🎯 Complete SEC + ESG Pipeline

**File**: `scrape_sec_and_analyze.py`

### Single Company (3 years)
```python
from scrape_sec_and_analyze import analyze_single_company

results = analyze_single_company("AAPL", num_years=3)
# Gets 3 proxy statements, analyzes ESG compensation for each
```

### Multiple Companies
```python
from scrape_sec_and_analyze import analyze_multiple_companies

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
df = analyze_multiple_companies(tickers, num_years=2)

# Returns pandas DataFrame with all results
df.to_csv("results.csv")
```

### Industry Analysis
```python
from scrape_sec_and_analyze import analyze_industry

# Analyze entire tech sector
tech = ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "AMD", "INTC"]
df = analyze_industry(tech, "Technology")

# Shows industry-wide ESG adoption statistics
```

**Run it**:
```bash
python3 scrape_sec_and_analyze.py
```

---

## 🔍 How It Works (Behind the Scenes)

```
1. YOUR CODE                2. edgartools          3. SEC EDGAR
   ↓                           ↓                       ↓
Company("AAPL")  →  Makes HTTP request  →  Returns filing data
   ↓                           ↓                       ↓
get_filings()    →  Parses SEC responses → SGML/XML/HTML files
   ↓                           ↓                       ↓
doc.text()       →  Extracts text       →  Clean text output
```

**No web scraping tools needed** - edgartools handles:
- ✅ HTTP requests to SEC
- ✅ Rate limiting (respects SEC rules)
- ✅ Parsing SGML/XML/HTML
- ✅ Text extraction
- ✅ Error handling

---

## 📋 Available Scripts

| Script | Purpose | SEC Data? | One-liner |
|--------|---------|-----------|-----------|
| **simple_sec_example.py** | Shortest example | ✅ | `python3 simple_sec_example.py` |
| **scrape_sec_and_analyze.py** | Full pipeline with ESG | ✅ | `python3 scrape_sec_and_analyze.py` |
| **sec_data_quick_guide.py** | Learn SEC API | ✅ | `python3 sec_data_quick_guide.py` |
| **run_esg_example.py** | ESG only (no SEC) | ❌ | `python3 run_esg_example.py` |

---

## 💻 Command Reference

### Get Company Info
```python
company = Company("AAPL")           # By ticker
company = Company("Apple Inc")      # By name
company = Company("0000320193")     # By CIK

print(company.name)
print(company.cik)
print(company.sic)
```

### Get Filings by Type
```python
# Proxy statements
company.get_filings(form="DEF 14A").latest(5)

# Annual reports
company.get_filings(form="10-K").latest(3)

# All filings
company.get_filings().latest(20)

# Date range
company.get_filings(
    form="8-K",
    filing_date="2023-01-01:2023-12-31"
)
```

### Extract Text
```python
filing = company.get_filings(form="DEF 14A").latest(1)[0]
doc = filing.primary_document

# Method 1: Plain text
text = doc.text()

# Method 2: HTML (with formatting)
html = doc.html()

# Get filing details
print(filing.filing_date)
print(filing.accession_number)
print(filing.homepage_url)
```

---

## 🎓 Example Use Cases

### 1. ESG Compensation Trends (2020-2024)
```python
company = Company("AAPL")
results = []

for year in range(2020, 2025):
    filings = company.get_filings(
        form="DEF 14A",
        filing_date=f"{year}-01-01:{year}-12-31"
    )
    
    if len(filings) > 0:
        filing = filings[0]
        text = filing.primary_document.text()
        result = process_proxy_statement(company.cik, year, text)
        results.append(result)

# Analyze ESG adoption over time
```

### 2. Industry Comparison
```python
industries = {
    "Tech": ["AAPL", "MSFT", "GOOGL"],
    "Energy": ["XOM", "CVX", "COP"],
    "Finance": ["JPM", "BAC", "WFC"]
}

for industry, tickers in industries.items():
    df = analyze_multiple_companies(tickers)
    print(f"{industry}: {df['ESG_PAY'].sum()} / {len(df)} use ESG pay")
```

### 3. S&P 500 Analysis
```python
# Get all S&P 500 tickers
sp500_tickers = ["AAPL", "MSFT", ...] # Full list

# Batch process
all_results = []
for ticker in sp500_tickers:
    try:
        results = analyze_single_company(ticker, num_years=1)
        all_results.extend(results)
    except:
        print(f"Skipping {ticker}")
    
    time.sleep(0.1)  # Be nice to SEC servers

# Save to CSV
pd.DataFrame(all_results).to_csv("sp500_esg_compensation.csv")
```

---

## 🚨 Important Notes

### SEC Rate Limits
- **Limit**: 10 requests per second
- **Solution**: edgartools automatically throttles requests
- **Best practice**: Add `time.sleep(0.1)` between companies if processing many

### Data Availability
- **Coverage**: Filings from 1994 onwards
- **Delay**: New filings appear within minutes of SEC publication
- **Format**: SGML (old), XML, HTML (varies by filing date)

### Text Extraction
Some filings are complex. Try both:
```python
try:
    text = doc.text()
except:
    text = doc.html()  # Fallback to HTML
```

---

## 📊 Output Example

```
ANALYZING: AAPL
======================================================================
Company: Apple Inc.
CIK: 0000320193

Fetching last 3 proxy statements from SEC EDGAR...
✓ Found 3 proxy statements

--- Filing 1/3 ---
Date: 2024-01-12
Accession: 0000320193-24-000006
✓ Extracted 523,184 characters
Analyzing ESG compensation...
ESG-Linked Pay: ✓ YES (high)
Score: 18.50
Top Terms: ESG modifier, diversity goals, emissions reduction targets

--- Filing 2/3 ---
Date: 2023-01-11
...

SUMMARY TABLE
======================================================================
ticker  year  ESG_PAY  ESG_PAY_confidence  ESG_PAY_SCORE
AAPL    2024        1                high          18.50
AAPL    2023        1                high          16.20
AAPL    2022        0                none           2.15
```

---

## ✅ Quick Start Checklist

- [ ] Install: `pip install edgartools pandas`
- [ ] Test basic: `python3 simple_sec_example.py`
- [ ] Test full pipeline: `python3 scrape_sec_and_analyze.py`
- [ ] Read guide: `sec_data_quick_guide.py`
- [ ] Customize tickers in scripts
- [ ] Run your analysis
- [ ] Export to CSV

---

## 🔗 Resources

### Official SEC
- **EDGAR Home**: https://www.sec.gov/edgar/
- **Search Companies**: https://www.sec.gov/edgar/searchedgar/companysearch
- **Filing Types**: https://www.sec.gov/forms

### edgartools
- **PyPI**: https://pypi.org/project/edgartools/
- **This Project**: Already integrated! Just `pip install edgartools`

### This Project
- **Installation**: `INSTALL_AND_RUN.md`
- **ESG API Docs**: `ESG_COMPENSATION_README.md`
- **All Scripts**: See `ESG_COMPENSATION_INDEX.md`

---

## 🎯 Bottom Line

**You DON'T need to:**
- ❌ Write web scrapers
- ❌ Parse HTML/XML manually
- ❌ Handle HTTP requests
- ❌ Get API keys
- ❌ Deal with rate limiting

**You JUST need to:**
- ✅ `pip install edgartools`
- ✅ `python3 simple_sec_example.py`
- ✅ Modify the ticker
- ✅ Done! 🎉

---

**Last Updated**: 2024-11-11  
**Status**: Production Ready ✅  
**No API Keys Required** | **Free** | **Real SEC Data**
