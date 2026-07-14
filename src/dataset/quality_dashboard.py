from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

from .dataset_balance import BalanceReport
from .dataset_health import HealthReport
from .dataset_quality import QualityResult
from .dataset_readiness import ReadinessResult


@dataclass
class DashboardData:
    generated_at: str = ""
    readiness: Optional[dict] = None
    quality: Optional[dict] = None
    health: Optional[dict] = None
    balance: Optional[dict] = None


class QualityDashboard:
    def generate_json(
        self,
        readiness: ReadinessResult,
        output_dir: str,
    ) -> str:
        data = DashboardData(
            generated_at=datetime.now().isoformat(),
            readiness=self._readiness_to_dict(readiness),
            quality=self._quality_to_dict(readiness.quality),
            health=self._health_to_dict(readiness.health),
            balance=self._balance_to_dict(readiness.balance),
        )

        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "dataset_quality.json")
        with open(path, "w") as f:
            json.dump(asdict(data), f, indent=2)

        health_path = os.path.join(output_dir, "dataset_health.json")
        health_data = self._health_to_dict(readiness.health) or {}
        with open(health_path, "w") as f:
            json.dump(health_data, f, indent=2)

        return path

    def generate_markdown(
        self,
        readiness: ReadinessResult,
        output_dir: str,
    ) -> str:
        lines: List[str] = []
        lines.append("# Dataset Quality Dashboard")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().isoformat()}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Readiness")
        lines.append("")
        status_marker = "[PASS]" if readiness.is_ready else "[FAIL]"
        lines.append(f"**Status:** {status_marker} {readiness.status}")
        lines.append("")
        lines.append(f"**Quality Score:** {readiness.quality_score:.1f}/100")
        lines.append("")

        if readiness.reasons:
            lines.append("### Issues")
            for r in readiness.reasons:
                lines.append(f"- {r}")
            lines.append("")

        if readiness.blocking_issues:
            lines.append("### Blocking Issues")
            for b in readiness.blocking_issues:
                lines.append(f"- {b}")
            lines.append("")

        if readiness.recommendations:
            lines.append("### Recommendations")
            for rec in readiness.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Dataset Quality")
        if readiness.quality:
            q = readiness.quality
            lines.append(f"- **Overall Score:** {q.overall_score:.1f}/100")
            lines.append(f"- **Label Completeness:** {q.label_completeness:.1f}%")
            lines.append(f"- **Image Integrity:** {q.image_integrity:.1f}%")
            lines.append(f"- **Format Compliance:** {q.format_compliance:.1f}%")
            lines.append(f"- **Resolution Compliance:** {q.resolution_compliance:.1f}%")
            lines.append(f"- **Aspect Ratio Compliance:** {q.aspect_ratio_compliance:.1f}%")
            lines.append(f"- **Total Images:** {q.total_images}")
            lines.append(f"- **Total Labels:** {q.total_labels}")
            lines.append(f"- **Valid Images:** {q.total_valid}")
            lines.append("")

            if q.corrupted_images:
                lines.append(f"**Corrupted Images ({len(q.corrupted_images)}):**")
                for img in q.corrupted_images[:10]:
                    lines.append(f"  - {img}")
                lines.append("")

            if q.missing_labels:
                lines.append(f"**Missing Labels ({len(q.missing_labels)}):**")
                for lbl in q.missing_labels[:10]:
                    lines.append(f"  - {lbl}")
                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Dataset Health")
        if readiness.health:
            h = readiness.health
            lines.append(f"- **Healthy:** {'Yes' if h.is_healthy else 'No'}")
            lines.append(f"- **Folder Structure:** {'OK' if h.folder_structure_ok else 'Issues'}")
            lines.append(f"- **Annotation Integrity:** {'OK' if h.annotation_integrity_ok else 'Issues'}")
            lines.append(f"- **Image Integrity:** {'OK' if h.image_integrity_ok else 'Issues'}")
            lines.append(f"- **Export Integrity:** {'OK' if h.export_integrity_ok else 'Issues'}")
            lines.append(f"- **Total Images Found:** {h.total_images}")
            lines.append(f"- **Total Labels Found:** {h.total_labels}")
            lines.append("")

            if h.issues:
                lines.append(f"**Issues ({len(h.issues)}):**")
                for issue in h.issues[:10]:
                    lines.append(f"  - {issue}")
                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Dataset Balance")
        if readiness.balance:
            b = readiness.balance
            lines.append(f"- **Imbalance Score:** {b.imbalance_score:.2f}")
            lines.append(f"- **Total Objects:** {b.total_objects}")
            lines.append(f"- **Total Images:** {b.total_images}")
            lines.append(f"- **Number of Classes:** {b.num_classes}")
            lines.append("")

            if b.objects_per_class:
                lines.append("### Objects per Class")
                for cls_name, count in b.objects_per_class.items():
                    lines.append(f"- {cls_name}: {count}")
                lines.append("")

            if b.split_distribution:
                lines.append("### Split Distribution")
                for split_name, count in b.split_distribution.items():
                    lines.append(f"- {split_name}: {count} labels")

        markdown = "\n".join(lines)
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "dataset_dashboard.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return path

    def generate_summary(self, readiness: ReadinessResult) -> str:
        lines: List[str] = []
        lines.append(f"Status: {readiness.status}")
        lines.append(f"Quality Score: {readiness.quality_score:.1f}/100")
        if readiness.reasons:
            lines.append(f"Issues: {len(readiness.reasons)}")
        if readiness.blocking_issues:
            lines.append(f"Blocking: {len(readiness.blocking_issues)}")
        if readiness.recommendations:
            lines.append(f"Recommendations: {len(readiness.recommendations)}")
        if readiness.quality:
            lines.append(
                f"Valid/Total Images: {readiness.quality.total_valid}/{readiness.quality.total_images}"
            )
        if readiness.balance:
            lines.append(f"Classes: {readiness.balance.num_classes}")
            lines.append(f"Total Objects: {readiness.balance.total_objects}")
            lines.append(f"Imbalance: {readiness.balance.imbalance_score:.2f}")
        return "\n".join(lines)

    def _readiness_to_dict(self, r: ReadinessResult) -> dict:
        return {
            "status": r.status,
            "quality_score": r.quality_score,
            "reasons": r.reasons,
            "recommendations": r.recommendations,
            "blocking_issues": r.blocking_issues,
        }

    def _quality_to_dict(self, q: Optional[QualityResult]) -> Optional[dict]:
        if q is None:
            return None
        return {
            "overall_score": q.overall_score,
            "label_completeness": q.label_completeness,
            "image_integrity": q.image_integrity,
            "format_compliance": q.format_compliance,
            "resolution_compliance": q.resolution_compliance,
            "aspect_ratio_compliance": q.aspect_ratio_compliance,
            "missing_labels": q.missing_labels,
            "empty_labels": q.empty_labels,
            "invalid_labels": q.invalid_labels,
            "corrupted_images": q.corrupted_images,
            "unsupported_formats": q.unsupported_formats,
            "resolution_issues": q.resolution_issues,
            "aspect_ratio_issues": q.aspect_ratio_issues,
            "total_images": q.total_images,
            "total_labels": q.total_labels,
            "total_valid": q.total_valid,
        }

    def _health_to_dict(self, h: Optional[HealthReport]) -> Optional[dict]:
        if h is None:
            return None
        return {
            "is_healthy": h.is_healthy,
            "folder_structure_ok": h.folder_structure_ok,
            "annotation_integrity_ok": h.annotation_integrity_ok,
            "image_integrity_ok": h.image_integrity_ok,
            "export_integrity_ok": h.export_integrity_ok,
            "issues": h.issues,
            "total_images": h.total_images,
            "total_labels": h.total_labels,
            "total_exports": h.total_exports,
        }

    def _balance_to_dict(self, b: Optional[BalanceReport]) -> Optional[dict]:
        if b is None:
            return None
        return {
            "objects_per_class": b.objects_per_class,
            "images_per_class": b.images_per_class,
            "split_distribution": b.split_distribution,
            "imbalance_score": b.imbalance_score,
            "total_objects": b.total_objects,
            "total_images": b.total_images,
            "num_classes": b.num_classes,
            "class_names": b.class_names,
        }
