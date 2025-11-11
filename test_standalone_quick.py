#!/usr/bin/env python3
"""Quick test of standalone script without SEC (no edgartools needed)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from esg_compensation_pipeline_all_in_one import process_proxy_statement

print("Testing ESG Classifier (No SEC data needed)")
print("="*60)

# Test with example text
proxy_text = """
Compensation Discussion and Analysis
Our executive compensation includes ESG-linked pay with an ESG modifier.
The annual bonus is tied to emissions reduction targets and diversity goals.
"""

result = process_proxy_statement("TEST_COMPANY", 2024, proxy_text)

print(f"✓ Import successful!")
print(f"✓ ESG-Linked: {result['ESG_PAY']}")
print(f"✓ Confidence: {result['ESG_PAY_confidence']}")
print(f"✓ Score: {result['ESG_PAY_SCORE']:.2f}")
print(f"✓ Matched: {', '.join(result['matched_terms'][:3])}")
print("\nNow you can use standalone_sec_esg_analysis.py for SEC data!")
