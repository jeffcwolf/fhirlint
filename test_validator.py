#!/usr/bin/env python3
"""Quick test of the bundle validator"""
import sys
sys.path.insert(0, '/work/src')

from validator import BundleValidator
import glob
import os

# Get first bundle file (filter out directories)
bundle_files = glob.glob('/work/data/**/*.json', recursive=True)
test_file = [f for f in bundle_files if os.path.isfile(f)][0]

print(f"Testing validator on: {test_file}\n")

# Create validator and test
validator = BundleValidator()
result = validator.load_bundle(test_file)

# Print results
print("=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)
print(f"File: {result['file_name']}")
print(f"Valid: {result['valid']}")
if result['error']:
    print(f"Error: {result['error']}")
print(f"Bundle Type: {result['bundle_type']}")
print(f"Entry Count: {result['entry_count']}")
print(f"Resource Types: {result['resource_types']}")
print(f"MII Modules: {result['mii_modules']}")
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(validator.get_summary(result))
print("\n" + "=" * 60)
print("STRUCTURAL ISSUES")
print("=" * 60)
issues = validator.validate_bundle_structure(result)
if issues:
    for issue in issues:
        print(f"  • {issue}")
else:
    print("  ✓ No structural issues found")
print("=" * 60)
