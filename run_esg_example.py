#!/usr/bin/env python3
"""
Simple example script to run ESG compensation classifier.
Just run: python3 run_esg_example.py
"""

from esg_compensation_pipeline_all_in_one import process_proxy_statement

# Example proxy statement text
proxy_text = """
Compensation Discussion and Analysis

Our executive compensation program is designed to align pay with performance.
The CEO and named executive officers receive compensation that includes 
ESG-linked pay with an ESG modifier.

The annual bonus plan incorporates the following metrics:
- Emissions reduction targets (25% weight)
- Diversity goals for leadership positions (15% weight)
- Safety performance measured by TRIR (10% weight)

The long-term incentive plan (LTIP) includes climate targets and 
renewable energy investment goals.
"""

# Process the proxy statement
result = process_proxy_statement("EXAMPLE_COMPANY", 2024, proxy_text)

# Display results
print("=" * 70)
print("ESG COMPENSATION ANALYSIS")
print("=" * 70)
print(f"\nCompany: EXAMPLE_COMPANY")
print(f"Year: 2024")
print(f"\n✓ ESG-Linked Compensation: {'YES' if result['ESG_PAY'] == 1 else 'NO'}")
print(f"✓ Confidence Level: {result['ESG_PAY_confidence'].upper()}")
print(f"✓ Classification Tier: {result['ESG_PAY_tier']}")

print(f"\n📊 ESG METRICS BREAKDOWN:")
print(f"   Environmental (E): {result['E_metrics']}")
print(f"   Social (S): {result['S_metrics']}")
print(f"   Governance (G): {result['G_metrics']}")

print(f"\n📈 SCORING:")
print(f"   Intensity Score: {result['ESG_PAY_INTENSITY']}")
print(f"   Breadth (categories): {result['ESG_PAY_BREADTH']}")
print(f"   Weighted Score: {result['ESG_PAY_SCORE']:.2f}")

print(f"\n🎯 MATCHED TERMS:")
for term in result['matched_terms'][:8]:
    print(f"   • {term}")

print(f"\n📋 ADDITIONAL INFO:")
print(f"   Applies to CEO: {result['applies_to_ceo']}")
print(f"   Mentions NEOs: {result['mentions_neo']}")
print(f"   CD&A Word Count: {result['cd_and_a_wordcount']:,}")

print("\n" + "=" * 70)
print("COMPLETE! Modify proxy_text variable to analyze your own data.")
print("=" * 70)
