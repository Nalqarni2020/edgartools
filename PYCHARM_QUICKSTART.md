# PyCharm Quick Start - 3 Simple Ways

## 🚀 Option 1: Run Demo (30 seconds)

### Step-by-Step:
1. **Open** `esg_compensation_pipeline_all_in_one.py` in PyCharm
2. **Click** Run → Edit Configurations (or Alt+Shift+F10)
3. **Set Parameters** to: `--demo`
4. **Click** OK
5. **Press** Shift+F10 (or click green Run button)

**Result**: You'll see the demo output with ESG classification results.

---

## 🎯 Option 2: Run Test File (Recommended)

### Step-by-Step:
1. **Open** `test_esg_local.py` in PyCharm
2. **Right-click** anywhere in the editor
3. **Select** "Run 'test_esg_local'"
4. **View** results in Run window (bottom panel)

**What it does**: Runs 4 different test cases showing various classification scenarios.

---

## 💻 Option 3: Python Console (Interactive)

### Step-by-Step:
1. **Open** Python Console: View → Tool Windows → Python Console (Alt+3)
2. **Copy and paste** this code:

```python
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Test text
text = """
Compensation Discussion and Analysis
CEO compensation includes ESG-linked pay with an ESG modifier.
Annual bonus tied to emissions reduction targets and diversity goals.
"""

# Analyze
result = process_proxy_statement("TEST", 2024, text)

# View results
print(f"ESG-Linked: {result['ESG_PAY']}")
print(f"Confidence: {result['ESG_PAY_confidence']}")
print(f"Matched Terms: {result['matched_terms']}")
```

3. **Press** Enter

---

## 📋 Run Configuration Template

### For CSV Processing:
1. Run → Edit Configurations → + → Python
2. Fill in:
   ```
   Name: ESG CSV Processor
   Script: /workspace/esg_compensation_pipeline_all_in_one.py
   Parameters: --input proxies.csv --output results.csv
   Working directory: /workspace
   ```
3. Click OK
4. Select from dropdown and Run

---

## 🔧 First Time Setup Checklist

- [ ] PyCharm project opened at `/workspace`
- [ ] Python 3.9+ interpreter selected (File → Settings → Project → Python Interpreter)
- [ ] `/workspace` marked as Sources Root (blue folder in Project view)
- [ ] Files visible in Project panel (left side)

---

## 🎓 What Each File Does

| File | Purpose | Run in PyCharm |
|------|---------|----------------|
| `esg_compensation_pipeline_all_in_one.py` | Main script | Right-click → Run (needs --demo parameter) |
| `test_esg_local.py` | **START HERE** - Ready to run tests | Right-click → Run ✅ |
| `esg_quick_start.py` | Code examples (prints patterns) | Right-click → Run |
| `tests/test_esg_compensation.py` | Unit tests | Right-click → Run (needs pytest) |
| `notebooks/esg_compensation_demo.ipynb` | Jupyter notebook | Open and Run All (Pro only) |

---

## 🚨 Troubleshooting

### "Cannot run program"
- Make sure Python interpreter is configured
- File → Settings → Project → Python Interpreter
- Select Python 3.9 or higher

### "Module not found"
- Right-click `/workspace` folder → Mark Directory as → Sources Root

### "No module named 'pandas'"
Optional dependencies for batch processing:
```bash
# In PyCharm Terminal (Alt+F12):
pip install pandas scikit-learn
```

### "No module named 'edgar'"
For edgartools integration:
```bash
pip install edgartools
```

---

## 💡 Pro Tips

### Run with Keyboard
- `Shift+F10` - Run current file
- `Ctrl+Shift+F10` - Run file under cursor
- `Shift+F9` - Debug current file

### Quick Navigation
- `Ctrl+N` - Find class/file by name
- `Ctrl+Shift+F` - Find in all files
- `Alt+F12` - Open terminal

### Debugging
1. Click in left gutter to set breakpoint (red dot)
2. Right-click → Debug
3. Use F8 (step over) and F7 (step into)

---

## 📖 Next Steps

1. **Run** `test_esg_local.py` to see it working
2. **Modify** the `proxy_text` variable with your own data
3. **Read** `PYCHARM_USAGE_GUIDE.md` for detailed instructions
4. **Check** `ESG_COMPENSATION_README.md` for API documentation

---

## 🎬 Quick Demo Video Steps

If making a screen recording:
1. Open PyCharm at `/workspace`
2. Open `test_esg_local.py`
3. Right-click → Run 'test_esg_local'
4. Show output in Run window
5. Modify `proxy_text` variable
6. Run again to show different results

**Total time: 2 minutes**
