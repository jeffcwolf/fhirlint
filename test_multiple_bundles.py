#!/usr/bin/env python3
"""Test validator on multiple bundles"""
import sys
sys.path.insert(0, '/work/src')

from validator import BundleValidator
import glob
import os

# Get first 10 bundle files
bundle_files = glob.glob('/work/data/**/*.json', recursive=True)
bundle_files = [f for f in bundle_files if os.path.isfile(f)][:10]

print(f"Testing validator on {len(bundle_files)} bundles\n")
print("=" * 80)

validator = BundleValidator()
results = []

for i, file_path in enumerate(bundle_files, 1):
    result = validator.load_bundle(file_path)
    results.append(result)

    status = "✓" if result['valid'] else "✗"
    print(f"{i}. {status} {result['file_name']}")
    print(f"   Resources: {result['entry_count']} | Types: {list(result['resource_types'].keys())}")
    print(f"   MII Modules: {result['mii_modules']}")
    if result['error']:
        print(f"   ERROR: {result['error']}")
    print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
valid_count = sum(1 for r in results if r['valid'])
print(f"Valid bundles: {valid_count}/{len(results)}")
print(f"Success rate: {(valid_count/len(results)*100):.1f}%")

# Collect all resource types
all_resource_types = set()
all_modules = set()
for r in results:
    all_resource_types.update(r['resource_types'].keys())
    all_modules.update(r['mii_modules'])

print(f"\nAll resource types found: {', '.join(sorted(all_resource_types))}")
print(f"All MII modules found: {', '.join(sorted(all_modules))}")
print("=" * 80)
