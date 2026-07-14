import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class DatasetReport:
    """Combine scanner, validator, and statistics results into structured JSON/Markdown reports."""

    def __init__(
        self,
        scanner_result: Optional[dict] = None,
        validator_result: Optional[dict] = None,
        statistics: Optional[dict] = None,
    ):
        self.scanner_result = scanner_result or {}
        self.validator_result = validator_result or {}
        self.statistics = statistics or {}
        self.generated_at = datetime.now().isoformat()

    def generate(self) -> dict:
        """Combine all results into a single comprehensive report dict."""
        return {
            "generated_at": self.generated_at,
            "scan": self.scanner_result,
            "validation": self.validator_result,
            "statistics": self.statistics,
        }

    def to_json(self, path: Optional[str | Path] = None, indent: int = 2) -> str:
        """Generate a JSON report, optionally writing to a file."""
        report = self.generate()
        json_str = json.dumps(report, indent=indent, default=str)

        if path:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json_str)

        return json_str

    def to_markdown(self, path: Optional[str | Path] = None) -> str:
        """Generate a Markdown report, optionally writing to a file."""
        lines = []

        lines.append("# Dataset Management Report")
        lines.append("")
        lines.append(f"**Generated at:** {self.generated_at}")
        lines.append("")

        # Scanner section
        lines.append("## Scanner Results")
        lines.append("")
        scan_summary = self.scanner_result.get("summary", {})
        if scan_summary:
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Images | {scan_summary.get('total_images', 0)} |")
            lines.append(f"| Total Labels | {scan_summary.get('total_labels', 0)} |")
            lines.append(f"| Missing Images | {scan_summary.get('total_missing_images', 0)} |")
            lines.append(f"| Missing Labels | {scan_summary.get('total_missing_labels', 0)} |")
            lines.append(f"| Duplicate Groups | {scan_summary.get('total_duplicate_groups', 0)} |")
            lines.append(f"| Unsupported Files | {scan_summary.get('total_unsupported', 0)} |")
            lines.append("")

        # Validator section
        lines.append("## Validation Results")
        lines.append("")
        val_summary = self.validator_result.get("summary", {})
        if val_summary:
            lines.append(f"**Passed:** {'Yes' if val_summary.get('passed') else 'No'}")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Errors | {val_summary.get('total_errors', 0)} |")
            lines.append(f"| Total Warnings | {val_summary.get('total_warnings', 0)} |")
            lines.append("")

        # Statistics section
        lines.append("## Dataset Statistics")
        lines.append("")
        stats = self.statistics
        if stats:
            lines.append("### Image Counts")
            lines.append("")
            total_imgs = stats.get("images", {}).get("total", 0)
            lines.append(f"Total images: {total_imgs}")
            per_split = stats.get("images", {}).get("per_split", {})
            for split, count in per_split.items():
                lines.append(f"- {split}: {count}")
            lines.append("")

            lines.append("### Dataset Size")
            lines.append("")
            lines.append(f"Total size: {stats.get('dataset_size_mb', 0)} MB")
            lines.append("")

            lines.append("### Resolution")
            lines.append("")
            avg = stats.get("average_resolution", {})
            lines.append(f"Average resolution: {avg.get('width', 0)}x{avg.get('height', 0)}")
            res_range = stats.get("resolution_range", {})
            w_range = res_range.get("width", {})
            h_range = res_range.get("height", {})
            lines.append(f"Width range: {w_range.get('min', 0)} - {w_range.get('max', 0)}")
            lines.append(f"Height range: {h_range.get('min', 0)} - {h_range.get('max', 0)}")
            lines.append("")

            lines.append("### Aspect Ratio Distribution")
            lines.append("")
            ar_dist = stats.get("aspect_ratio_distribution", {})
            if ar_dist:
                lines.append("| Aspect Ratio | Count |")
                lines.append("|--------------|-------|")
                for bucket, count in ar_dist.items():
                    lines.append(f"| {bucket} | {count} |")
            else:
                lines.append("No data available.")
            lines.append("")

            lines.append("### Label Counts")
            lines.append("")
            labels = stats.get("labels", {})
            lines.append(f"Total labels: {labels.get('total', 0)}")
            lines.append(f"Total annotations: {labels.get('total_annotations', 0)}")
            lines.append("")

        # Issues section
        lines.append("## Issues")
        lines.append("")

        missing_imgs = self.scanner_result.get("missing_images", [])
        if missing_imgs:
            lines.append("### Missing Images")
            lines.append("")
            for m in missing_imgs:
                lines.append(f"- `{m['stem']}` in split `{m['split']}`")
            lines.append("")

        missing_lbls = self.scanner_result.get("missing_labels", [])
        if missing_lbls:
            lines.append("### Missing Labels")
            lines.append("")
            for m in missing_lbls:
                lines.append(f"- `{m['stem']}` in split `{m['split']}`")
            lines.append("")

        dups = self.scanner_result.get("duplicates", [])
        if dups:
            lines.append("### Duplicate Files")
            lines.append("")
            for d in dups:
                lines.append(f"- Hash `{d['hash'][:12]}...`: {len(d['files'])} copies")
                for f in d["files"]:
                    lines.append(f"  - `{f}`")
            lines.append("")

        unsupported_files = self.scanner_result.get("unsupported", [])
        if unsupported_files:
            lines.append("### Unsupported Formats")
            lines.append("")
            for u in unsupported_files:
                lines.append(f"- `{u['path']}` (extension: `{u.get('extension', '?')}`)")
            lines.append("")

        val_errors: list[dict] = []
        val_warnings: list[dict] = []

        for item in self.validator_result.get("structure", []):
            if item["level"] == "error":
                val_errors.append(item)
            else:
                val_warnings.append(item)

        for split_issues in self.validator_result.get("labels", {}).values():
            for issue in split_issues:
                if issue["level"] == "error":
                    val_errors.append(issue)
                else:
                    val_warnings.append(issue)

        for split_issues in self.validator_result.get("images", {}).values():
            for issue in split_issues:
                if issue["level"] == "error":
                    val_errors.append(issue)
                else:
                    val_warnings.append(issue)

        for split_issues in self.validator_result.get("naming", {}).values():
            for issue in split_issues:
                if issue["level"] == "error":
                    val_errors.append(issue)
                else:
                    val_warnings.append(issue)

        for item in self.validator_result.get("split_integrity", []):
            if item["level"] == "error":
                val_errors.append(item)
            else:
                val_warnings.append(item)

        if val_errors:
            lines.append("### Validation Errors")
            lines.append("")
            for e in val_errors:
                file_info = f" in `{e['file']}`" if e.get("file") else ""
                line_info = f" (line {e['line']})" if e.get("line") else ""
                lines.append(f"- {e['message']}{file_info}{line_info}")
            lines.append("")

        if val_warnings:
            lines.append("### Validation Warnings")
            lines.append("")
            for w in val_warnings:
                file_info = f" in `{w.get('file', '')}`" if w.get("file") else ""
                lines.append(f"- {w['message']}{file_info}")
            lines.append("")

        if not missing_imgs and not missing_lbls and not dups and not unsupported_files and not val_errors and not val_warnings:
            lines.append("No issues found.")
            lines.append("")

        report = "\n".join(lines)

        if path:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report)

        return report
