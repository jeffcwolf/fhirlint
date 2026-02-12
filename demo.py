#!/usr/bin/env python3
"""
FHIR Quality Inspector Demo
Processes a sample of bundles and generates reports
"""
import sys
sys.path.insert(0, '/work/src')

import glob
import os
from pathlib import Path
from validator import BundleValidator
from quality_checker import QualityChecker
from report_generator import ReportGenerator


def main():
    print("=" * 80)
    print("🏥 FHIR QUALITY INSPECTOR - DEMO")
    print("=" * 80)
    print("\nProcessing sample POLAR FHIR bundles...\n")

    # Get sample bundles (first 50 for demo)
    bundle_files = glob.glob('/work/data/**/*.json', recursive=True)
    bundle_files = [f for f in bundle_files if os.path.isfile(f)][:50]

    print(f"Found {len(bundle_files)} bundles to process\n")

    # Initialize components
    validator = BundleValidator()
    quality_checker = QualityChecker()
    report_generator = ReportGenerator()

    # Process bundles
    results = []
    for i, file_path in enumerate(bundle_files, 1):
        print(f"[{i}/{len(bundle_files)}] Processing {Path(file_path).name}...", end=' ')

        # Validate
        bundle_result = validator.load_bundle(file_path)

        if not bundle_result['valid']:
            print(f"❌ Failed: {bundle_result['error']}")
            results.append({'bundle': bundle_result, 'quality': None})
            continue

        # Quality check
        quality_result = quality_checker.check_bundle(bundle_result['bundle_data'])

        results.append({
            'bundle': bundle_result,
            'quality': quality_result
        })

        status = "✓" if quality_result['passed'] else "✗"
        print(f"{status} Score: {quality_result['quality_score']}%")

    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    total = len(results)
    valid = sum(1 for r in results if r['bundle']['valid'])
    passed = sum(1 for r in results if r['quality'] and r['quality']['passed'])

    avg_score = 0
    if valid > 0:
        scores = [r['quality']['quality_score'] for r in results if r['quality']]
        avg_score = sum(scores) / len(scores) if scores else 0

    total_errors = sum(r['quality']['errors'] for r in results if r['quality'])
    total_warnings = sum(r['quality']['warnings'] for r in results if r['quality'])

    print(f"Total bundles: {total}")
    print(f"Valid bundles: {valid}/{total} ({valid/total*100:.1f}%)")
    print(f"Passed quality: {passed}/{valid} ({passed/valid*100:.1f}%)")
    print(f"Average quality score: {avg_score:.1f}%")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")

    # Generate reports
    print("\n" + "=" * 80)
    print("📄 GENERATING REPORTS")
    print("=" * 80)

    output_dir = Path('/work/output')
    output_dir.mkdir(exist_ok=True)

    html_file, json_file = report_generator.generate_reports(results, str(output_dir))

    print(f"✓ HTML report: {html_file}")
    print(f"✓ JSON report: {json_file}")

    print("\n" + "=" * 80)
    print("✓ DEMO COMPLETE")
    print("=" * 80)
    print(f"\nOpen the HTML report in your browser to see the results!")
    print(f"  file://{html_file}\n")


if __name__ == "__main__":
    main()
