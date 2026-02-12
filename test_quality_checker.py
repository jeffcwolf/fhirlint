#!/usr/bin/env python3
"""Test quality checker on bundles"""
import sys
sys.path.insert(0, '/work/src')

from validator import BundleValidator
from quality_checker import QualityChecker
import glob
import os

# Get first 5 bundle files
bundle_files = glob.glob('/work/data/**/*.json', recursive=True)
bundle_files = [f for f in bundle_files if os.path.isfile(f)][:5]

print(f"Testing quality checker on {len(bundle_files)} bundles\n")
print("=" * 80)

validator = BundleValidator()
quality_checker = QualityChecker()

for i, file_path in enumerate(bundle_files, 1):
    # Load bundle
    bundle_result = validator.load_bundle(file_path)

    if not bundle_result['valid']:
        print(f"{i}. ✗ {bundle_result['file_name']} - Failed to parse")
        continue

    # Run quality checks
    quality_result = quality_checker.check_bundle(bundle_result['bundle_data'])

    # Display results
    print(f"\n{i}. {bundle_result['file_name']}")
    print(f"   Resources: {bundle_result['entry_count']}")
    print(f"   Quality Score: {quality_result['quality_score']}%")
    print(f"   Checks: {quality_result['checks_passed']}/{quality_result['checks_performed']} passed")
    print(f"   Issues: {quality_result['errors']} errors, "
          f"{quality_result['warnings']} warnings, {quality_result['infos']} info")

    # Show first 5 issues
    if quality_result['issues']:
        print(f"\n   Top issues:")
        for issue in quality_result['issues'][:5]:
            severity_icon = {"error": "✗", "warning": "⚠", "info": "ℹ"}.get(issue['severity'], "·")
            print(f"      {severity_icon} [{issue['severity'].upper()}] {issue['description']}")
            if issue['resource_type']:
                print(f"        → {issue['resource_type']}/{issue['resource_id']}")

    if bundle_result['schema_errors']:
        print(f"\n   Schema validation issues detected (FHIR spec strict checking)")

    print(f"   Status: {'✓ PASSED' if quality_result['passed'] else '✗ FAILED (has errors)'}")

print("\n" + "=" * 80)
