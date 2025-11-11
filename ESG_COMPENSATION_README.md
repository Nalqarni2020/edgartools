# ESG Compensation Classification Pipeline

A dictionary-based classifier for identifying and analyzing ESG-linked executive compensation in SEC proxy statements (DEF 14A filings).

## Overview

This tool analyzes proxy statement text to detect whether executive compensation packages include Environmental, Social, and Governance (ESG) metrics. It provides:

- **Binary classification** (ESG-linked or not)
- **Confidence scoring** (high/medium/none)
- **Intensity metrics** (E/S/G component counts)
- **Weighted scoring** for research applications
- **Edge case detection** (greenwashing, governance-only mentions, CEO-specific indicators)

## Features

### Multi-Tier Dictionary Matching

- **Tier 1**: High-confidence terms (e.g., "ESG-linked compensation", "ESG modifier", "TRIR")
- **Tier 2**: Context-dependent terms requiring proximity to compensation keywords (e.g., "climate targets", "diversity goals")
- **Tier 3**: General sustainability terms used for intensity scoring

### Classification Outputs

The `process_proxy_statement()` function returns a dictionary with:

| Field | Description |
|-------|-------------|
| `ESG_PAY` | Binary indicator (1=ESG-linked, 0=not linked, None=no CD&A found) |
| `ESG_PAY_confidence` | Confidence level: "high", "medium", "none", or "missing_cd_and_a" |
| `ESG_PAY_tier` | Which tier triggered the classification (1, 2, or 3) |
| `matched_terms` | List of specific ESG terms found |
| `E_metrics`, `S_metrics`, `G_metrics` | Counts of environmental, social, governance terms |
| `ESG_PAY_INTENSITY` | Total ESG term count |
| `ESG_PAY_BREADTH` | Number of ESG categories represented (0-3) |
| `ESG_PAY_SCORE` | Weighted score based on term confidence |
| `ESG_PAY_weighted_binary` | Binary classification using weighted threshold |
| `cd_and_a_wordcount` | Size of CD&A section |
| `cd_and_a_found` | Whether CD&A section was extracted |
| `applies_to_ceo` | Whether CEO is explicitly mentioned |
| `mentions_neo` | Whether Named Executive Officers are mentioned |
| `governance_vs_compensation_flag` | Distinguishes governance oversight from compensation linkage |

## Usage

### As a Python Module

```python
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Process a single proxy statement
proxy_text = """
Compensation Discussion and Analysis
Our executive compensation includes ESG-linked metrics...
"""

result = process_proxy_statement(
    firm_id="AAPL",
    year=2024,
    proxy_text=proxy_text
)

print(f"ESG-linked: {result['ESG_PAY']}")
print(f"Confidence: {result['ESG_PAY_confidence']}")
print(f"Matched terms: {result['matched_terms']}")
```

### Integration with edgartools

```python
from edgar import Company
from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Get company and filings
company = Company("AAPL")
def14a_filings = company.get_filings(form="DEF 14A").latest(5)

# Process each proxy statement
results = []
for filing in def14a_filings:
    # Extract text from primary document
    doc = filing.primary_document
    if doc:
        proxy_text = doc.text()  # or doc.html() depending on format
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
```

### Command-Line Interface

```bash
# Run demo example
python3 esg_compensation_pipeline_all_in_one.py --demo

# Process a CSV file
python3 esg_compensation_pipeline_all_in_one.py \
    --input proxies.csv \
    --output results.csv
```

Input CSV format:
- Columns: `firm_id`, `year`, `proxy_text`
- `proxy_text` should contain the full proxy statement text

## Methodology

### Section Extraction

The pipeline first extracts the "Compensation Discussion and Analysis" (CD&A) section, which is the primary location for executive compensation disclosures.

### Term Matching with Context

1. **Tier 1 Terms**: Matched directly; require proximity to compensation keywords
2. **Tier 2 Terms**: Must appear within 200 words of compensation-related terms
3. **Tier 3 Terms**: Used for intensity scoring and supplementary analysis

### Compensation Keywords

The following terms indicate compensation-related context:
- compensation, incentive, bonus, pay
- annual incentive plan (AIP)
- long-term incentive (LTIP, LTI)
- short-term incentive (STIP, STI)

### Edge Case Handling

- **Greenwashing Detection**: Filters generic sustainability statements
- **Governance vs. Compensation**: Distinguishes board oversight from pay linkage
- **CEO-Specific Indicators**: Flags whether compensation applies to CEO specifically

## Validation

The pipeline includes helper functions for validation:

```python
from esg_compensation_pipeline_all_in_one import compute_validation_metrics

manual_labels = [1, 0, 1, 0, 1, 1, 0, 0]
auto_labels = [1, 0, 1, 1, 1, 1, 0, 0]

metrics = compute_validation_metrics(manual_labels, auto_labels)
print(f"Precision: {metrics['precision']:.2f}")
print(f"Recall: {metrics['recall']:.2f}")
print(f"F1 Score: {metrics['f1']:.2f}")
```

## Limitations

1. **Dictionary-Based**: May miss novel or creative ESG compensation structures
2. **English-Only**: Designed for US SEC filings in English
3. **Text-Dependent**: Requires clean text extraction from PDF/HTML
4. **Context-Sensitive**: Performance depends on CD&A section extraction quality

## Research Applications

This tool is designed for academic and industry research on ESG-linked executive compensation, including:

- Trend analysis across industries and time periods
- Correlation studies with firm performance
- ESG rating validation
- Regulatory compliance analysis

## Dependencies

- **Required**: None (pure Python stdlib)
- **Optional**: 
  - `pandas` for CSV batch processing
  - `scikit-learn` for validation metrics

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies (if using pytest)
pip install pytest

# Run tests
pytest tests/test_esg_compensation.py -v
```

## Citation

If you use this tool in research, please cite:

```bibtex
@software{esg_compensation_pipeline,
  title = {ESG Compensation Classification Pipeline},
  year = {2024},
  url = {https://github.com/dgunning/edgartools}
}
```

## License

MIT License - See LICENSE.txt for details

## Contributing

Contributions welcome! Areas for improvement:
- Additional ESG terms and categories
- Industry-specific dictionaries
- Machine learning integration
- Multi-language support
- Enhanced section extraction algorithms

## Contact

For questions or collaboration opportunities related to this ESG compensation classifier, please open an issue on the edgartools GitHub repository.
