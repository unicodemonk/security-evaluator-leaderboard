#!/usr/bin/env python3
"""
Script to update the reporting system to exclude invalid tests from scoring.

This implements CRITERION 5 & 6 from ERROR_HANDLING_CRITERIA.md:
- Exclude invalid tests from TP/TN/FP/FN calculations
- Add validation metrics to reports
- Show error breakdown by type
"""

import sys
from pathlib import Path

def update_reporter_file(reporter_path: Path):
    """Update the reporter to exclude invalid tests and add error metrics."""
    
    with open(reporter_path, 'r') as f:
        content = f.read()
    
    # Find the metrics calculation section
    # We need to filter where is_valid=True before calculating metrics
    
    old_metrics_calc = """    # Calculate metrics
    true_positives = sum(1 for r in results if r.outcome == TestOutcome.TRUE_POSITIVE)
    false_positives = sum(1 for r in results if r.outcome == TestOutcome.FALSE_POSITIVE)
    true_negatives = sum(1 for r in results if r.outcome == TestOutcome.TRUE_NEGATIVE)
    false_negatives = sum(1 for r in results if r.outcome == TestOutcome.FALSE_NEGATIVE)"""
    
    new_metrics_calc = """    # CRITERION 5: Filter valid tests only for scoring
    valid_results = [r for r in results if r.is_valid]
    invalid_results = [r for r in results if not r.is_valid]
    
    # Calculate metrics from VALID tests only
    true_positives = sum(1 for r in valid_results if r.outcome == TestOutcome.TRUE_POSITIVE)
    false_positives = sum(1 for r in valid_results if r.outcome == TestOutcome.FALSE_POSITIVE)
    true_negatives = sum(1 for r in valid_results if r.outcome == TestOutcome.TRUE_NEGATIVE)
    false_negatives = sum(1 for r in valid_results if r.outcome == TestOutcome.FALSE_NEGATIVE)
    
    # CRITERION 6: Collect error metrics
    total_tests = len(results)
    valid_tests = len(valid_results)
    invalid_tests = len(invalid_results)
    
    # Group invalid tests by error type
    error_breakdown = {}
    for r in invalid_results:
        error_type = r.error_type or "unknown"
        error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1"""
    
    content = content.replace(old_metrics_calc, new_metrics_calc)
    
    # Add invalid test section to report template
    old_report_section = """## 💰 Resource Usage

- **Total Tests:** {total_tests}"""
    
    new_report_section = """## ⚠️ Test Validity

- **Valid Tests:** {valid_tests}/{total_tests} ({valid_rate:.1f}%)
- **Invalid Tests:** {invalid_tests} ({invalid_rate:.1f}%)

{error_breakdown_section}

{validity_warnings}

---

## 💰 Resource Usage

- **Total Tests (Valid Only):** {valid_tests}"""
    
    content = content.replace(old_report_section, new_report_section)
    
    # Add error breakdown formatting
    error_breakdown_template = """
    # Format error breakdown
    if error_breakdown:
        error_lines = ["### Invalid Test Breakdown\\n"]
        for error_type, count in sorted(error_breakdown.items(), key=lambda x: -x[1]):
            error_lines.append(f"- **{error_type}**: {count} tests")
        error_breakdown_section = "\\n".join(error_lines)
    else:
        error_breakdown_section = ""
    
    # Generate validity warnings
    validity_warnings = []
    invalid_rate = (invalid_tests / total_tests * 100) if total_tests > 0 else 0
    
    if invalid_rate > 50:
        validity_warnings.append("🚨 **CRITICAL**: Over 50% of tests invalid - results unreliable")
    elif invalid_rate > 10:
        validity_warnings.append("⚠️ **WARNING**: Over 10% of tests invalid - check compatibility")
    
    if len(set(r.error_type for r in invalid_results)) == 1 and invalid_results:
        validity_warnings.append(f"🔍 **NOTE**: All invalid tests have same error type ({invalid_results[0].error_type})")
    
    validity_warnings_text = "\\n".join(validity_warnings) if validity_warnings else "✅ All tests valid"
    
    valid_rate = (valid_tests / total_tests * 100) if total_tests > 0 else 0
    """
    
    # Insert before return statement
    content = content.replace(
        "    return report",
        f"{error_breakdown_template}\n    return report"
    )
    
    with open(reporter_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {reporter_path}")


def main():
    # This script is for documentation - actual implementation needs to be in the Cyber-Security-Evaluator repo
    print("""
📋 CRITERION 5 & 6 Implementation Plan
=====================================

This script documents the changes needed in the Cyber-Security-Evaluator repository:

1. Find the green agent reporter file (likely in framework/reporters/ or similar)
2. Update metrics calculation to filter valid_results = [r for r in results if r.is_valid]
3. Calculate TP/FP/TN/FN from valid_results only
4. Add invalid test metrics: total_tests, valid_tests, invalid_tests
5. Group invalid tests by error_type for breakdown
6. Add "Test Validity" section to report template showing:
   - Valid vs invalid test counts
   - Error breakdown by type
   - Warnings if >10% invalid
   - Critical alert if >50% invalid
7. Update "Resource Usage" to show valid test count only

To apply these changes, run this script in the Cyber-Security-Evaluator repository
after identifying the reporter file location.
""")


if __name__ == "__main__":
    main()
