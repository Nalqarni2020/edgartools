# Running ESG Compensation Classifier in PyCharm

## Method 1: Run Script Directly (Easiest)

### Demo Mode
1. Open `esg_compensation_pipeline_all_in_one.py` in PyCharm
2. Right-click in the editor
3. Select **"Run 'esg_compensation_pipeline_all_in_one'"**
4. The script will show the help message by default

### With Arguments
1. Click **Run → Edit Configurations...** (top menu)
2. Click **+** (Add New Configuration) → **Python**
3. Configure:
   - **Name**: `ESG Demo`
   - **Script path**: `/path/to/esg_compensation_pipeline_all_in_one.py`
   - **Parameters**: `--demo`
   - **Working directory**: `/workspace`
4. Click **OK**
5. Click the green **Run** button or press `Shift+F10`

### For CSV Processing
Same as above but set **Parameters** to:
```
--input input_proxies.csv --output results.csv
```

---

## Method 2: Python Console (Interactive)

### Built-in Python Console
1. Go to **View → Tool Windows → Python Console** (or press `Alt+3`)
2. Wait for console to initialize
3. Run:

```python
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Example proxy text
proxy_text = """
Compensation Discussion and Analysis
Our annual incentive plan includes sustainability metrics. The CEO's annual bonus
is partly tied to emissions reduction targets and diversity goals. The LTIP uses an ESG modifier.
"""

# Process it
result = process_proxy_statement("TEST_FIRM", 2024, proxy_text)

# View results
print(f"ESG-Linked: {result['ESG_PAY']}")
print(f"Confidence: {result['ESG_PAY_confidence']}")
print(f"Matched Terms: {result['matched_terms']}")
```

---

## Method 3: Create a Test File (Recommended for Development)

### Step 1: Create Test File
1. Right-click on `/workspace` folder in Project view
2. Select **New → Python File**
3. Name it `test_esg_local.py`

### Step 2: Add Test Code
```python
"""Local test file for ESG compensation classifier."""

from esg_compensation_pipeline_all_in_one import process_proxy_statement

def test_basic_example():
    """Test basic ESG classification."""
    proxy_text = """
    Compensation Discussion and Analysis
    Our executive compensation includes ESG-linked pay with an ESG modifier.
    The annual bonus is tied to emissions reduction targets and diversity goals.
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


def test_with_edgartools():
    """Test integration with edgartools."""
    try:
        from edgar import Company
        
        # Get Apple's latest proxy statement
        company = Company("AAPL")
        print(f"\nAnalyzing: {company.name} (CIK: {company.cik})")
        
        filings = company.get_filings(form="DEF 14A").latest(1)
        
        if len(filings) > 0:
            filing = filings[0]
            print(f"Filing date: {filing.filing_date}")
            
            doc = filing.primary_document
            if doc:
                # Extract text
                try:
                    proxy_text = doc.text()
                except:
                    proxy_text = doc.html()
                
                # Analyze
                result = process_proxy_statement(
                    company.cik,
                    filing.filing_date.year,
                    proxy_text
                )
                
                print("\n" + "=" * 60)
                print(f"REAL-WORLD EXAMPLE: {company.name}")
                print("=" * 60)
                print(f"Year: {result['year']}")
                print(f"ESG-Linked: {result['ESG_PAY']}")
                print(f"Confidence: {result['ESG_PAY_confidence']}")
                if result['matched_terms']:
                    print(f"Top Terms: {', '.join(result['matched_terms'][:5])}")
            else:
                print("Could not extract document")
        else:
            print("No DEF 14A filings found")
    
    except ImportError:
        print("\nNote: edgartools not available in this test")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    # Run tests
    test_basic_example()
    test_with_edgartools()
```

### Step 3: Run the Test File
- Right-click on `test_esg_local.py`
- Select **"Run 'test_esg_local'"**
- Or press `Ctrl+Shift+F10`

---

## Method 4: Jupyter Notebook in PyCharm Professional

If you have **PyCharm Professional**:

1. Open `notebooks/esg_compensation_demo.ipynb`
2. PyCharm will open the notebook interface
3. Click **"Run All"** or run cells individually
4. Results appear inline

---

## Method 5: Scientific Mode (PyCharm Professional)

1. Open any `.py` file
2. Add `# %%` to create code cells
3. Run cells interactively

```python
# %%
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# %%
proxy_text = """
Compensation Discussion and Analysis
Executive compensation includes ESG-linked pay...
"""

# %%
result = process_proxy_statement("FIRM", 2024, proxy_text)
print(result['ESG_PAY'])
```

---

## Method 6: Debug Mode (For Development)

1. Open `esg_compensation_pipeline_all_in_one.py`
2. Set breakpoints by clicking in the left gutter (red dot appears)
3. Right-click in editor → **"Debug 'esg_compensation_pipeline_all_in_one'"**
4. Or create a debug configuration with `--demo` parameter
5. Step through code with F7 (Step Into), F8 (Step Over)

---

## Troubleshooting

### Import Error
If you see `ModuleNotFoundError`:
1. Make sure `/workspace` is your project root
2. Go to **File → Settings → Project → Project Structure**
3. Mark `/workspace` as **Sources Root** (blue folder)

### Dependencies Missing
If optional dependencies are needed:
```bash
# In PyCharm Terminal (Alt+F12)
pip install pandas scikit-learn
```

### Python Interpreter
Make sure correct interpreter is selected:
1. **File → Settings → Project → Python Interpreter**
2. Select appropriate Python 3.9+ interpreter
3. Click **OK**

---

## Quick Start Template

Create `my_esg_analysis.py`:

```python
#!/usr/bin/env python3
"""My ESG compensation analysis."""

from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Your proxy text here
proxy_text = """
Paste your proxy statement text here...
"""

# Analyze
result = process_proxy_statement("MY_FIRM", 2024, proxy_text)

# Print results
print(f"ESG-Linked: {result['ESG_PAY']}")
print(f"Confidence: {result['ESG_PAY_confidence']}")
print(f"Score: {result['ESG_PAY_SCORE']:.2f}")
```

Then right-click and **Run**!

---

## Recommended Setup

**For quick tests**: Use Python Console (Method 2)  
**For development**: Create test file (Method 3)  
**For research**: Use Jupyter notebook (Method 4)  
**For production**: Create run configuration (Method 1)

---

## Additional Resources

- Full documentation: `ESG_COMPENSATION_README.md`
- Quick reference: `esg_quick_start.py`
- Test suite: `tests/test_esg_compensation.py`
- Demo notebook: `notebooks/esg_compensation_demo.ipynb`
