#!/usr/bin/env python3
"""
FHIR Quality Inspector - Main Application
Desktop application for validating FHIR bundles against MII standards
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import glob
import os
import json
from pathlib import Path
from typing import List
import threading

from validator import BundleValidator
from quality_checker import QualityChecker
from report_generator import ReportGenerator


class FHIRQualityInspector:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("FHIR Quality Inspector - MII Kerndatensatz Validator")
        self.root.geometry("1000x700")

        # Initialize components
        self.validator = BundleValidator()
        self.quality_checker = QualityChecker()
        self.report_generator = ReportGenerator()

        # Results storage
        self.results = []
        self.processing = False

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the user interface"""
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)

        title = ttk.Label(
            header_frame,
            text="🏥 FHIR Quality Inspector",
            font=("Arial", 18, "bold")
        )
        title.pack(side=tk.LEFT)

        subtitle = ttk.Label(
            header_frame,
            text="MII Kerndatensatz Validation & Quality Analysis",
            font=("Arial", 10)
        )
        subtitle.pack(side=tk.LEFT, padx=20)

        # Control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # File selection
        ttk.Label(control_frame, text="Select FHIR Bundles:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        self.path_var = tk.StringVar(value="No files selected")
        path_label = ttk.Label(control_frame, textvariable=self.path_var, foreground="gray")
        path_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Select Files...", command=self._select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Select Folder...", command=self._select_folder).pack(side=tk.LEFT, padx=5)
        self.process_btn = ttk.Button(
            btn_frame, text="▶ Process Bundles", command=self._process_bundles, style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Export Report", command=self._export_report).pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            control_frame, variable=self.progress_var, maximum=100, mode='determinate'
        )
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.status_var = tk.StringVar(value="Ready to process bundles")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W)

        # Results area
        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(results_frame, text="Results:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg="#f5f5f5"
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Configure text tags for colors
        self.results_text.tag_config("header", foreground="#2563eb", font=("Courier", 10, "bold"))
        self.results_text.tag_config("success", foreground="#16a34a")
        self.results_text.tag_config("error", foreground="#dc2626")
        self.results_text.tag_config("warning", foreground="#ea580c")
        self.results_text.tag_config("info", foreground="#6b7280")

        # Selected files
        self.selected_files = []

    def _select_files(self):
        """Select individual FHIR bundle files"""
        files = filedialog.askopenfilenames(
            title="Select FHIR Bundle JSON Files",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            self.path_var.set(f"{len(self.selected_files)} file(s) selected")
            self._log(f"Selected {len(self.selected_files)} files", "info")

    def _select_folder(self):
        """Select folder containing FHIR bundles"""
        folder = filedialog.askdirectory(title="Select Folder with FHIR Bundles")
        if folder:
            # Find all JSON files in folder
            json_files = glob.glob(os.path.join(folder, "**/*.json"), recursive=True)
            self.selected_files = [f for f in json_files if os.path.isfile(f)]
            self.path_var.set(f"{len(self.selected_files)} file(s) found in folder")
            self._log(f"Found {len(self.selected_files)} JSON files in {folder}", "info")

    def _process_bundles(self):
        """Process selected FHIR bundles"""
        if not self.selected_files:
            self._log("❌ No files selected. Please select files or a folder first.", "error")
            return

        if self.processing:
            self._log("⚠ Already processing bundles. Please wait...", "warning")
            return

        # Clear previous results
        self.results = []
        self.results_text.delete(1.0, tk.END)

        # Run processing in background thread
        self.processing = True
        self.process_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._process_bundles_thread, daemon=True)
        thread.start()

    def _process_bundles_thread(self):
        """Process bundles in background thread"""
        total = len(self.selected_files)

        self._log_safe("=" * 80, "header")
        self._log_safe("🔍 FHIR QUALITY INSPECTION STARTED", "header")
        self._log_safe("=" * 80, "header")
        self._log_safe(f"\nProcessing {total} bundles...\n")

        for i, file_path in enumerate(self.selected_files):
            # Update progress
            progress = (i / total) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda i=i, t=total: self.status_var.set(f"Processing {i+1}/{t}..."))

            # Validate bundle
            bundle_result = self.validator.load_bundle(file_path)

            if not bundle_result['valid']:
                self._log_safe(f"\n❌ {bundle_result['file_name']}", "error")
                self._log_safe(f"   Error: {bundle_result['error']}", "error")
                self.results.append({
                    'bundle': bundle_result,
                    'quality': None
                })
                continue

            # Run quality checks
            quality_result = self.quality_checker.check_bundle(bundle_result['bundle_data'])

            # Store results
            self.results.append({
                'bundle': bundle_result,
                'quality': quality_result
            })

            # Log results
            status_icon = "✓" if quality_result['passed'] else "✗"
            tag = "success" if quality_result['passed'] else "error"

            self._log_safe(f"\n{status_icon} {bundle_result['file_name']}", tag)
            self._log_safe(f"   Quality Score: {quality_result['quality_score']}% "
                          f"({quality_result['checks_passed']}/{quality_result['checks_performed']} checks passed)")

            if quality_result['total_issues'] > 0:
                self._log_safe(f"   Issues: {quality_result['errors']} errors, "
                              f"{quality_result['warnings']} warnings, {quality_result['infos']} info",
                              "warning" if quality_result['errors'] == 0 else "error")

        # Finish
        self.root.after(0, lambda: self.progress_var.set(100))
        self.root.after(0, lambda: self.status_var.set("✓ Processing complete"))

        # Show summary
        self._show_summary()

        self.processing = False
        self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))

    def _show_summary(self):
        """Show summary statistics"""
        total = len(self.results)
        valid_bundles = sum(1 for r in self.results if r['bundle']['valid'])
        passed_quality = sum(1 for r in self.results if r['quality'] and r['quality']['passed'])

        avg_score = 0
        if valid_bundles > 0:
            scores = [r['quality']['quality_score'] for r in self.results if r['quality']]
            avg_score = sum(scores) / len(scores) if scores else 0

        total_issues = sum(r['quality']['total_issues'] for r in self.results if r['quality'])
        total_errors = sum(r['quality']['errors'] for r in self.results if r['quality'])
        total_warnings = sum(r['quality']['warnings'] for r in self.results if r['quality'])

        self._log_safe("\n" + "=" * 80, "header")
        self._log_safe("📊 SUMMARY STATISTICS", "header")
        self._log_safe("=" * 80, "header")
        self._log_safe(f"\nTotal bundles processed: {total}")
        self._log_safe(f"Valid bundles: {valid_bundles}/{total} ({valid_bundles/total*100:.1f}%)")
        self._log_safe(f"Passed quality checks: {passed_quality}/{valid_bundles} "
                      f"({passed_quality/valid_bundles*100:.1f}%)" if valid_bundles > 0 else "N/A")
        self._log_safe(f"Average quality score: {avg_score:.1f}%")
        self._log_safe(f"\nTotal issues found: {total_issues}")
        self._log_safe(f"  Errors: {total_errors}", "error" if total_errors > 0 else "success")
        self._log_safe(f"  Warnings: {total_warnings}", "warning" if total_warnings > 0 else "info")
        self._log_safe("\n" + "=" * 80, "header")

    def _export_report(self):
        """Export results to HTML/JSON"""
        if not self.results:
            self._log("⚠ No results to export. Please process bundles first.", "warning")
            return

        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory for Reports")
        if not output_dir:
            return

        self._log(f"\n📄 Generating reports in {output_dir}...")

        # Generate reports
        html_file, json_file = self.report_generator.generate_reports(self.results, output_dir)

        self._log(f"✓ HTML report: {html_file}", "success")
        self._log(f"✓ JSON report: {json_file}", "success")
        self._log(f"\n✓ Reports generated successfully!", "success")

    def _log(self, message: str, tag: str = ""):
        """Log message to results area"""
        self.results_text.insert(tk.END, message + "\n", tag)
        self.results_text.see(tk.END)
        self.root.update_idletasks()

    def _log_safe(self, message: str, tag: str = ""):
        """Thread-safe logging"""
        self.root.after(0, lambda: self._log(message, tag))


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set style
    style = ttk.Style()
    style.theme_use('clam')

    app = FHIRQualityInspector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
