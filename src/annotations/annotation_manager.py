from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set

from .annotation_exporter import AnnotationExporter
from .annotation_statistics import AnnotationStatistics, AnnotationStatsResult
from .annotation_validator import AnnotationValidationResult, AnnotationValidator
from .dataset_consistency_checker import ConsistencyResult, DatasetConsistencyChecker
from .label_inspector import LabelInspectionResult, LabelInspector


@dataclass
class AnnotationStudioReport:
    label_dir: str
    image_dir: Optional[str] = None
    validated_files: List[AnnotationValidationResult] = field(default_factory=list)
    inspection: Optional[LabelInspectionResult] = None
    consistency: Optional[ConsistencyResult] = None
    statistics: Optional[AnnotationStatsResult] = None
    total_valid_files: int = 0
    total_invalid_files: int = 0
    total_objects: int = 0
    issues_found: bool = False
    generated_at: str = ""
    export_paths: Dict[str, str] = field(default_factory=dict)


class AnnotationManager:
    def __init__(
        self,
        allowed_classes: Optional[List[int]] = None,
        class_names: Optional[Dict[int, str]] = None,
    ):
        self.validator = AnnotationValidator(allowed_classes=allowed_classes)
        self.inspector = LabelInspector(allowed_classes=allowed_classes)
        self.checker = DatasetConsistencyChecker(allowed_classes=allowed_classes)
        self.statistics = AnnotationStatistics(allowed_classes=allowed_classes)
        self.exporter = AnnotationExporter()
        self.allowed_classes = allowed_classes
        self.class_names = class_names or {}

    def run(
        self,
        label_dir: str,
        image_dir: Optional[str] = None,
        image_extensions: Optional[Set[str]] = None,
        export_dir: Optional[str] = None,
    ) -> AnnotationStudioReport:
        if image_extensions is None:
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

        report = AnnotationStudioReport(
            label_dir=label_dir,
            image_dir=image_dir,
            generated_at=datetime.now().isoformat(),
        )

        validated_files = self._validate_all(label_dir)
        report.validated_files = validated_files
        report.total_valid_files = sum(1 for v in validated_files if v.is_valid)
        report.total_invalid_files = sum(1 for v in validated_files if not v.is_valid)
        report.total_objects = sum(v.valid_objects for v in validated_files)

        if image_dir:
            report.inspection = self.inspector.inspect(
                label_dir=label_dir,
                image_dir=image_dir,
                image_extensions=image_extensions,
            )
            report.consistency = self.checker.check(
                label_dir=label_dir,
                image_dir=image_dir,
                image_extensions=image_extensions,
                class_names=self.class_names,
            )

        report.statistics = self.statistics.compute(
            label_dir=label_dir,
            class_names=self.class_names,
        )

        report.issues_found = (
            report.total_invalid_files > 0
            or (report.inspection is not None and report.inspection.issues_found)
            or (report.consistency is not None and not report.consistency.is_consistent)
        )

        if export_dir:
            os.makedirs(export_dir, exist_ok=True)
            report.export_paths["validation"] = self.exporter.export_validation_to_json(
                validated_files, os.path.join(export_dir, "validation.json")
            )
            if report.inspection:
                report.export_paths["inspection"] = self.exporter.export_inspection_to_json(
                    report.inspection, os.path.join(export_dir, "inspection.json")
                )
            if report.consistency:
                report.export_paths["consistency"] = self.exporter.export_consistency_to_json(
                    report.consistency, os.path.join(export_dir, "consistency.json")
                )
            if report.statistics:
                report.export_paths["statistics"] = self.exporter.export_statistics_to_json(
                    report.statistics, os.path.join(export_dir, "statistics.json")
                )
            report.export_paths["summary"] = self.exporter.export_summary_to_markdown(
                stats=report.statistics,
                consistency=report.consistency,
                inspection=report.inspection,
                output_path=os.path.join(export_dir, "annotation_summary.md"),
            )

        return report

    def _validate_all(self, label_dir: str) -> List[AnnotationValidationResult]:
        if not os.path.isdir(label_dir):
            return []
        label_files = sorted([
            f for f in os.listdir(label_dir)
            if os.path.isfile(os.path.join(label_dir, f))
            and f.lower().endswith(".txt")
            and not f.startswith(".")
        ])
        return [self.validator.validate_file(os.path.join(label_dir, f)) for f in label_files]
