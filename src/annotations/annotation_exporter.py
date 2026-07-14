from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from .annotation_statistics import AnnotationStatsResult
from .annotation_validator import AnnotationValidationResult
from .dataset_consistency_checker import ConsistencyResult
from .label_inspector import LabelInspectionResult


class AnnotationExporter:
    def export_validation_to_json(
        self, results: List[AnnotationValidationResult], output_path: str
    ) -> str:
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_files": len(results),
            "valid_count": sum(1 for r in results if r.is_valid),
            "invalid_count": sum(1 for r in results if not r.is_valid),
            "files": [
                {
                    "file_path": r.file_path,
                    "is_valid": r.is_valid,
                    "total_objects": r.total_objects,
                    "valid_objects": r.valid_objects,
                    "is_empty": r.is_empty,
                    "errors": r.errors,
                    "lines": [
                        {
                            "line_number": lr.line_number,
                            "is_valid": lr.is_valid,
                            "errors": lr.errors,
                            "class_id": lr.class_id,
                            "x_center": lr.x_center,
                            "y_center": lr.y_center,
                            "width": lr.width,
                            "height": lr.height,
                        }
                        for lr in r.line_results
                    ],
                }
                for r in results
            ],
        }
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return output_path

    def export_inspection_to_json(
        self, result: LabelInspectionResult, output_path: str
    ) -> str:
        data = {
            "exported_at": datetime.now().isoformat(),
            "label_dir": result.label_dir,
            "image_dir": result.image_dir,
            "total_labels": result.total_labels,
            "total_images": result.total_images,
            "valid_labels": result.valid_labels,
            "invalid_labels": result.invalid_labels,
            "issues_found": result.issues_found,
            "missing_labels": sorted(result.missing_labels),
            "orphaned_labels": sorted(result.orphaned_labels),
            "empty_labels": sorted(result.empty_labels),
            "invalid_class_ids": {
                k: sorted(v) for k, v in result.invalid_class_ids.items()
            },
            "out_of_bounds_files": result.out_of_bounds_files,
        }
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return output_path

    def export_consistency_to_json(
        self, result: ConsistencyResult, output_path: str
    ) -> str:
        data = {
            "exported_at": datetime.now().isoformat(),
            "label_dir": result.label_dir,
            "image_dir": result.image_dir,
            "total_images": result.total_images,
            "total_labels": result.total_labels,
            "paired": result.paired,
            "unmatched_images": result.unmatched_images,
            "unmatched_labels": result.unmatched_labels,
            "class_distribution": result.class_distribution,
            "class_names": result.class_names,
            "issues": result.issues,
            "is_consistent": result.is_consistent,
        }
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return output_path

    def export_statistics_to_json(
        self, result: AnnotationStatsResult, output_path: str
    ) -> str:
        def _stats_to_dict(stats):
            if stats is None:
                return None
            return {
                "min": stats.min,
                "max": stats.max,
                "mean": stats.mean,
                "median": stats.median,
                "std": stats.std,
            }

        data = {
            "exported_at": datetime.now().isoformat(),
            "label_dir": result.label_dir,
            "total_files": result.total_files,
            "total_objects": result.total_objects,
            "objects_per_image": _stats_to_dict(result.objects_per_image_stats),
            "class_distribution": result.class_distribution,
            "class_names": result.class_names,
            "bbox_width": _stats_to_dict(result.bbox_width_stats),
            "bbox_height": _stats_to_dict(result.bbox_height_stats),
            "bbox_area": _stats_to_dict(result.bbox_area_stats),
            "aspect_ratio_buckets": result.aspect_ratio_buckets,
        }
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return output_path

    def export_summary_to_markdown(
        self,
        stats: Optional[AnnotationStatsResult] = None,
        consistency: Optional[ConsistencyResult] = None,
        inspection: Optional[LabelInspectionResult] = None,
        output_path: Optional[str] = None,
    ) -> str:
        lines = ["# Annotation Studio Summary", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        if stats:
            lines.append("## Annotation Statistics")
            lines.append("")
            lines.append(f"- Total label files: {stats.total_files}")
            lines.append(f"- Total objects: {stats.total_objects}")
            if stats.objects_per_image_stats:
                o = stats.objects_per_image_stats
                lines.append(
                    f"- Objects per image: min={o.min}, max={o.max}, "
                    f"mean={o.mean}, median={o.median}, std={o.std}"
                )
            lines.append("")
            if stats.class_distribution:
                lines.append("### Class Distribution")
                lines.append("")
                lines.append("| Class ID | Name | Count |")
                lines.append("|---------|------|-------|")
                total = sum(stats.class_distribution.values())
                for cid, cnt in stats.class_distribution.items():
                    name = stats.class_names.get(cid, f"class_{cid}")
                    pct = f"({cnt / total * 100:.1f}%)" if total > 0 else ""
                    lines.append(f"| {cid} | {name} | {cnt} {pct} |")
                lines.append("")
            if stats.aspect_ratio_buckets:
                lines.append("### Bounding Box Aspect Ratios")
                lines.append("")
                lines.append("| Category | Count |")
                lines.append("|----------|-------|")
                for cat, cnt in stats.aspect_ratio_buckets.items():
                    if cnt > 0:
                        lines.append(f"| {cat} | {cnt} |")
                lines.append("")

        if consistency:
            lines.append("## Dataset Consistency")
            lines.append("")
            lines.append(f"- Total images: {consistency.total_images}")
            lines.append(f"- Total labels: {consistency.total_labels}")
            lines.append(f"- Paired: {consistency.paired}")
            lines.append(f"- Unmatched images: {len(consistency.unmatched_images)}")
            lines.append(f"- Unmatched labels: {len(consistency.unmatched_labels)}")
            lines.append(f"- Consistent: {consistency.is_consistent}")
            if consistency.issues:
                lines.append("")
                lines.append("### Issues")
                for issue in consistency.issues:
                    lines.append(f"- {issue}")
            lines.append("")

        if inspection:
            lines.append("## Label Inspection")
            lines.append("")
            lines.append(f"- Total labels: {inspection.total_labels}")
            lines.append(f"- Valid labels: {inspection.valid_labels}")
            lines.append(f"- Invalid labels: {inspection.invalid_labels}")
            lines.append(f"- Empty labels: {len(inspection.empty_labels)}")
            lines.append(f"- Missing labels: {len(inspection.missing_labels)}")
            lines.append(f"- Orphaned labels: {len(inspection.orphaned_labels)}")
            if inspection.empty_labels:
                lines.append("")
                lines.append("### Empty Label Files")
                for f in inspection.empty_labels:
                    lines.append(f"- {f}")
            if inspection.missing_labels:
                lines.append("")
                lines.append("### Missing Labels (images without annotations)")
                for f in inspection.missing_labels:
                    lines.append(f"- {f}")
            if inspection.orphaned_labels:
                lines.append("")
                lines.append("### Orphaned Labels (labels without images)")
                for f in inspection.orphaned_labels:
                    lines.append(f"- {f}")
            lines.append("")

        content = "\n".join(lines)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w") as f:
                f.write(content)
            return output_path

        return content
