#!/usr/bin/env python3
"""
ESG COMPENSATION CLASSIFIER - COPY AND RUN THIS!
Just save this file and run: python3 COPY_THIS_SCRIPT.py
"""

from esg_compensation_pipeline_all_in_one import process_proxy_statement

# YOUR PROXY TEXT HERE - Replace this with your actual proxy statement
proxy_text = """
Compensation Discussion and Analysis

Our executive compensation includes ESG-linked pay with an ESG modifier.
The annual bonus is tied to emissions reduction targets and diversity goals.
Safety performance is measured using TRIR.
"""

# ANALYZE IT
result = process_proxy_statement("YOUR_COMPANY", 2024, proxy_text)

# SHOW RESULTS
print("\n" + "="*60)
print("ESG COMPENSATION RESULTS")
print("="*60)
print(f"ESG-Linked: {'YES ✓' if result['ESG_PAY']==1 else 'NO ✗'}")
print(f"Confidence: {result['ESG_PAY_confidence']}")
print(f"Score: {result['ESG_PAY_SCORE']:.2f}")
print(f"\nMatched Terms: {', '.join(result['matched_terms'][:5])}")
print(f"\nE/S/G Metrics: {result['E_metrics']}/{result['S_metrics']}/{result['G_metrics']}")
print("="*60 + "\n")
