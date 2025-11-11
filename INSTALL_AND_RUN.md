# 📥 Install & Run - SEC Data Extraction + ESG Analysis

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
# Install edgartools (for SEC data access)
pip install edgartools

# Optional: For CSV processing and metrics
pip install pandas scikit-learn
```

### Step 2: Run Examples
```bash
# Option A: Quick SEC data guide (shows how to get SEC filings)
python3 sec_data_quick_guide.py

# Option B: Full SEC + ESG analysis
python3 scrape_sec_and_analyze.py

# Option C: Just ESG analysis (no SEC needed)
python3 run_esg_example.py
```

### Step 3: Modify for Your Research
Edit the tickers in any script:
```python
tickers = ["AAPL", "MSFT", "GOOGL"]  # Change these!
```

---

## 📚 What Each Script Does

| Script | SEC Data? | ESG Analysis? | Description |
|--------|-----------|---------------|-------------|
| **sec_data_quick_guide.py** | ✅ | ❌ | Learn SEC EDGAR API |
| **scrape_sec_and_analyze.py** | ✅ | ✅ | Full pipeline: Get proxy → Analyze ESG |
| **run_esg_example.py** | ❌ | ✅ | ESG analysis only (no SEC) |
| **COPY_THIS_SCRIPT.py** | ❌ | ✅ | Minimal ESG example |

---

## 🔧 Installation Details

### Using pip (Recommended)
```bash
pip install edgartools pandas scikit-learn
```

### Using conda
```bash
conda install -c conda-forge pandas scikit-learn
pip install edgartools
```

### Check if installed
```bash
python3 -c "import edgar; print('edgartools:', edgar.__version__)"
python3 -c "import pandas; print('pandas:', pandas.__version__)"
```

---

## 🎯 Complete Example (Copy & Run)

Save as `my_sec_analysis.py`:

```python
#!/usr/bin/env python3
"""Get Apple's proxy from SEC and analyze ESG compensation."""

from edgar import Company
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# 1. Get company from SEC
company = Company("AAPL")
print(f"Analyzing: {company.name}")

# 2. Get latest proxy statement
filings = company.get_filings(form="DEF 14A").latest(1)

if len(filings) > 0:
    filing = filings[0]
    print(f"Filing date: {filing.filing_date}")
    
    # 3. Extract text
    doc = filing.primary_document
    proxy_text = doc.text()
    print(f"Extracted {len(proxy_text):,} characters")
    
    # 4. Analyze ESG compensation
    result = process_proxy_statement(
        company.cik,
        filing.filing_date.year,
        proxy_text
    )
    
    # 5. Show results
    print(f"\nESG-Linked: {result['ESG_PAY']}")
    print(f"Confidence: {result['ESG_PAY_confidence']}")
    print(f"Score: {result['ESG_PAY_SCORE']:.2f}")
    print(f"Terms: {result['matched_terms'][:5]}")
else:
    print("No proxy statements found")
```

Run it:
```bash
python3 my_sec_analysis.py
```

---

## 🌐 SEC EDGAR Access (No API Key Needed!)

**edgartools** accesses SEC's public EDGAR database:
- ✅ **Free** - No API keys required
- ✅ **Official data** - Direct from SEC.gov
- ✅ **Real-time** - Latest filings as they're published
- ✅ **Historical** - All filings back to 1994

### What You Can Get:
- **Proxy Statements** (DEF 14A) - Executive compensation
- **Annual Reports** (10-K) - Full financials
- **Quarterly Reports** (10-Q) - Quarterly financials
- **Current Reports** (8-K) - Major events
- **Insider Trading** (Forms 3, 4, 5)
- And 100+ other filing types

---

## 📊 Example Outputs

### Single Company Analysis
```
ANALYZING: AAPL
============================================================
Company: Apple Inc.
CIK: 0000320193

Fetching last 3 proxy statements from SEC EDGAR...
✓ Found 3 proxy statements

--- Filing 1/3 ---
Date: 2024-01-12
✓ Extracted 523,184 characters
ESG-Linked Pay: ✓ YES (high)
Score: 18.50
Top Terms: ESG modifier, diversity goals, emissions reduction
```

### Multiple Company Comparison
```
SUMMARY TABLE
============================================================
ticker  year  ESG_PAY  ESG_PAY_confidence  ESG_PAY_SCORE  ESG_PAY_INTENSITY
AAPL    2024        1                high          18.50                  4
MSFT    2024        1                high          22.30                  5
GOOGL   2024        1              medium          12.75                  3
```

---

## 🚨 Troubleshooting

### "No module named 'httpx'" or "No module named 'edgar'"
```bash
pip install edgartools
```

### "No module named 'pandas'"
```bash
pip install pandas
```

### Rate limits or connection errors
edgartools respects SEC rate limits automatically. If you hit limits:
- Wait a few minutes
- Reduce batch size
- Add delays: `time.sleep(0.1)` between requests

### Proxy text extraction fails
Try both methods:
```python
try:
    text = doc.text()
except:
    text = doc.html()
```

---

## 💡 Research Workflow

### 1. **Exploratory** (Start here)
```bash
python3 sec_data_quick_guide.py
```
Learn how to access SEC data

### 2. **Single Company** (Test your approach)
```bash
python3 scrape_sec_and_analyze.py
# Edit to analyze just 1 company
```

### 3. **Batch Processing** (Scale up)
```python
tickers = ["AAPL", "MSFT", ...100 more...]
df = analyze_multiple_companies(tickers)
df.to_csv("results.csv")
```

### 4. **Time Series** (Trends over time)
```python
results = analyze_single_company("AAPL", num_years=10)
# Analyze ESG adoption trends
```

---

## 📖 Additional Resources

### SEC EDGAR
- Website: https://www.sec.gov/edgar/
- Search companies: https://www.sec.gov/edgar/searchedgar/companysearch
- Filing types: https://www.sec.gov/forms

### edgartools Documentation
- PyPI: https://pypi.org/project/edgartools/
- GitHub: https://github.com/dgunning/edgartools
- Docs: Check project README

### This Project
- ESG Classifier: `ESG_COMPENSATION_README.md`
- PyCharm Guide: `PYCHARM_QUICKSTART.md`
- Quick Reference: `USAGE_SUMMARY.md`

---

## ✅ Quick Health Check

Run this to verify everything works:

```bash
# Test 1: Check installations
python3 -c "import edgar; print('✓ edgartools installed')"
python3 -c "import pandas; print('✓ pandas installed')"
python3 -c "from esg_compensation_pipeline_all_in_one import process_proxy_statement; print('✓ ESG classifier ready')"

# Test 2: Quick ESG analysis (no SEC needed)
python3 COPY_THIS_SCRIPT.py

# Test 3: SEC data access (requires edgartools)
python3 -c "from edgar import Company; c=Company('AAPL'); print(f'✓ SEC access OK: {c.name}')"

# Test 4: Full pipeline (SEC + ESG)
python3 scrape_sec_and_analyze.py
```

---

## 🎓 Next Steps

1. ✅ Install: `pip install edgartools pandas`
2. ✅ Test: `python3 sec_data_quick_guide.py`
3. ✅ Analyze: `python3 scrape_sec_and_analyze.py`
4. ✅ Customize: Edit tickers and parameters
5. ✅ Export: Save results to CSV
6. ✅ Research: Analyze trends, industries, time series

**You're ready to analyze ESG compensation across the entire S&P 500!** 🚀

---

**Last Updated**: 2024-11-11  
**Status**: Production Ready ✅
