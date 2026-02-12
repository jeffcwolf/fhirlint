"""
Report Generator for FHIR Quality Inspector
Generates HTML and JSON reports
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple


class ReportGenerator:
    """Generates quality inspection reports"""

    def generate_reports(self, results: List[Dict[str, Any]], output_dir: str) -> Tuple[str, str]:
        """
        Generate HTML and JSON reports

        Args:
            results: List of validation/quality results
            output_dir: Directory to save reports

        Returns:
            Tuple of (html_file_path, json_file_path)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir)

        # Generate JSON report
        json_file = output_path / f"fhir_quality_report_{timestamp}.json"
        self._generate_json_report(results, json_file)

        # Generate HTML report
        html_file = output_path / f"fhir_quality_report_{timestamp}.html"
        self._generate_html_report(results, html_file)

        return str(html_file), str(json_file)

    def _generate_json_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Generate machine-readable JSON report"""
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_bundles': len(results),
            'summary': self._calculate_summary(results),
            'bundles': []
        }

        for result in results:
            bundle_info = result['bundle']
            quality_info = result.get('quality')

            bundle_report = {
                'file_name': bundle_info['file_name'],
                'valid': bundle_info['valid'],
                'bundle_type': bundle_info['bundle_type'],
                'entry_count': bundle_info['entry_count'],
                'resource_types': bundle_info['resource_types'],
                'mii_modules': bundle_info['mii_modules'],
            }

            if quality_info:
                bundle_report['quality'] = quality_info

            if bundle_info.get('error'):
                bundle_report['error'] = bundle_info['error']

            report_data['bundles'].append(bundle_report)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _generate_html_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Generate human-readable HTML report"""
        summary = self._calculate_summary(results)

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FHIR Quality Inspection Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #2563eb;
        }}
        .stat-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
        }}
        .stat-subtext {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 4px;
        }}
        .success {{ color: #16a34a; }}
        .error {{ color: #dc2626; }}
        .warning {{ color: #ea580c; }}
        .content {{
            padding: 30px;
        }}
        h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            color: #1f2937;
        }}
        .bundle-list {{
            display: grid;
            gap: 15px;
        }}
        .bundle-card {{
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 20px;
            transition: box-shadow 0.2s;
        }}
        .bundle-card:hover {{
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .bundle-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
        }}
        .bundle-name {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
        }}
        .bundle-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-passed {{
            background: #dcfce7;
            color: #16a34a;
        }}
        .status-failed {{
            background: #fee2e2;
            color: #dc2626;
        }}
        .bundle-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 12px;
            font-size: 13px;
        }}
        .meta-item {{
            color: #6b7280;
        }}
        .meta-item strong {{
            color: #1f2937;
        }}
        .issues {{
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e5e7eb;
        }}
        .issue-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 8px;
            font-weight: 500;
        }}
        .badge-error {{
            background: #fee2e2;
            color: #dc2626;
        }}
        .badge-warning {{
            background: #fed7aa;
            color: #ea580c;
        }}
        .badge-info {{
            background: #e0e7ff;
            color: #4f46e5;
        }}
        .footer {{
            padding: 20px 30px;
            background: #f9fafb;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 FHIR Quality Inspection Report</h1>
            <p>MII Kerndatensatz Validation Results</p>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">Total Bundles</div>
                <div class="stat-value">{summary['total_bundles']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pass Rate</div>
                <div class="stat-value {'success' if summary['pass_rate'] >= 90 else 'warning' if summary['pass_rate'] >= 70 else 'error'}">
                    {summary['pass_rate']:.1f}%
                </div>
                <div class="stat-subtext">{summary['passed']}/{summary['valid_bundles']} passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Quality Score</div>
                <div class="stat-value">{summary['avg_quality_score']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Issues</div>
                <div class="stat-value {'success' if summary['total_issues'] == 0 else 'warning'}">
                    {summary['total_issues']}
                </div>
                <div class="stat-subtext">
                    <span class="error">{summary['total_errors']} errors</span> ·
                    <span class="warning">{summary['total_warnings']} warnings</span>
                </div>
            </div>
        </div>

        <div class="content">
            <h2>Bundle Details</h2>
            <div class="bundle-list">
"""

        # Add bundle cards
        for result in results:
            bundle = result['bundle']
            quality = result.get('quality')

            status_class = 'passed' if quality and quality['passed'] else 'failed'
            status_text = '✓ Passed' if quality and quality['passed'] else '✗ Failed'

            html += f"""
                <div class="bundle-card">
                    <div class="bundle-header">
                        <div class="bundle-name">{bundle['file_name']}</div>
                        <div class="bundle-status status-{status_class}">{status_text}</div>
                    </div>
"""

            if quality:
                html += f"""
                    <div class="bundle-meta">
                        <div class="meta-item"><strong>Quality Score:</strong> {quality['quality_score']}%</div>
                        <div class="meta-item"><strong>Resources:</strong> {bundle['entry_count']}</div>
                        <div class="meta-item"><strong>Bundle Type:</strong> {bundle['bundle_type']}</div>
                        <div class="meta-item"><strong>MII Modules:</strong> {', '.join(bundle['mii_modules']) if bundle['mii_modules'] else 'None'}</div>
                    </div>
"""

                if quality['total_issues'] > 0:
                    html += """
                    <div class="issues">
"""
                    if quality['errors'] > 0:
                        html += f'<span class="issue-badge badge-error">{quality["errors"]} errors</span>'
                    if quality['warnings'] > 0:
                        html += f'<span class="issue-badge badge-warning">{quality["warnings"]} warnings</span>'
                    if quality['infos'] > 0:
                        html += f'<span class="issue-badge badge-info">{quality["infos"]} info</span>'
                    html += """
                    </div>
"""

            if bundle.get('error'):
                html += f"""
                    <div class="issues">
                        <span class="error">Error: {bundle['error']}</span>
                    </div>
"""

            html += """
                </div>
"""

        html += """
            </div>
        </div>

        <div class="footer">
            Generated by FHIR Quality Inspector | MII Kerndatensatz Validator
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

    def _calculate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total = len(results)
        valid_bundles = sum(1 for r in results if r['bundle']['valid'])
        passed = sum(1 for r in results if r.get('quality') and r['quality']['passed'])

        avg_score = 0
        if valid_bundles > 0:
            scores = [r['quality']['quality_score'] for r in results if r.get('quality')]
            avg_score = sum(scores) / len(scores) if scores else 0

        total_issues = sum(r['quality']['total_issues'] for r in results if r.get('quality'))
        total_errors = sum(r['quality']['errors'] for r in results if r.get('quality'))
        total_warnings = sum(r['quality']['warnings'] for r in results if r.get('quality'))

        pass_rate = (passed / valid_bundles * 100) if valid_bundles > 0 else 0

        return {
            'total_bundles': total,
            'valid_bundles': valid_bundles,
            'passed': passed,
            'pass_rate': pass_rate,
            'avg_quality_score': avg_score,
            'total_issues': total_issues,
            'total_errors': total_errors,
            'total_warnings': total_warnings
        }
