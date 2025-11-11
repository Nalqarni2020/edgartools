# ESG Compensation Classifier - Usage Summary

## Quick Test
```bash
python3 esg_compensation_pipeline_all_in_one.py --demo
```

## Import in Python
```python
from esg_compensation_pipeline_all_in_one import process_proxy_statement

result = process_proxy_statement(firm_id, year, proxy_text)
# Returns dict with ESG_PAY, confidence, matched_terms, metrics, etc.
```

## Key Output Fields
- `ESG_PAY`: 1 (yes), 0 (no), None (no CD&A found)
- `ESG_PAY_confidence`: "high", "medium", "none"
- `ESG_PAY_tier`: 1 (explicit), 2 (contextual), 3 (none)
- `matched_terms`: List of detected ESG terms
- `E_metrics`, `S_metrics`, `G_metrics`: Environmental/Social/Governance counts
- `ESG_PAY_INTENSITY`: Total ESG metric count
- `ESG_PAY_SCORE`: Weighted confidence score

## Files
- `esg_compensation_pipeline_all_in_one.py` - Main script
- `ESG_COMPENSATION_README.md` - Full documentation
- `tests/test_esg_compensation.py` - Test suite (14 tests)
- `notebooks/esg_compensation_demo.ipynb` - Interactive examples
- `esg_quick_start.py` - Code examples

## Classification Tiers
1. **Tier 1** (High Confidence): "ESG-linked compensation", "ESG modifier", "TRIR", etc.
2. **Tier 2** (Medium Confidence): "climate targets", "diversity goals" (must be near compensation terms)
3. **Tier 3** (Context Only): Generic "sustainability", "ESG" mentions

## Example with edgartools
```python
from edgar import Company
from esg_compensation_pipeline_all_in_one import process_proxy_statement

company = Company("AAPL")
filings = company.get_filings(form="DEF 14A").latest(3)

for filing in filings:
    doc = filing.primary_document
    if doc:
        result = process_proxy_statement(
            company.cik, 
            filing.filing_date.year,
            doc.text()
        )
        print(f"{filing.filing_date.year}: ESG_PAY={result['ESG_PAY']}")
```

## Status
✅ All tests passing (14/14)
✅ Demo working
✅ Jupyter-safe (uses parse_known_args)
✅ Production ready
