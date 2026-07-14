from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import cv2
import numpy as np


@dataclass
class HealthReport:
    is_healthy: bool = True
    issues: List[str] = field(default_factory=list)
    folder_structure_ok: bool = True
    annotation_integrity_ok: bool = True
    image_integrity_ok: bool = True
    export_integrity_ok: bool = True
    folder_structure_issues: List[str] = field(default_factory=list)
    annotation_integrity_issues: List[str] = field(default_factory=list)
    image_integrity_issues: List[str] = field(default_factory=list)
    export_integrity_issues: List[str] = field(default_factory=list)
    total_images: int = 0
    total_labels: int = 0
    total_exports: int = 0


class DatasetHealth:
    REQUIRED_DIRS = ["train", "val", "test"]
    REQUIRED_SUBDIRS = ["images", "labels"]

    def analyze(
        self,
        dataset_root: str,
        export_dir: Optional[str] = None,
    ) -> HealthReport:
        report = HealthReport()

        self._check_folder_structure(dataset_root, report)
        self._check_annotation_integrity(dataset_root, report)
        self._check_image_integrity(dataset_root, report)
        self._check_export_integrity(export_dir, report)

        report.is_healthy = (
            report.folder_structure_ok
            and report.annotation_integrity_ok
            and report.image_integrity_ok
            and report.export_integrity_ok
        )
        report.issues = (
            report.folder_structure_issues
            + report.annotation_integrity_issues
            + report.image_integrity_issues
            + report.export_integrity_issues
        )
        return report

    def _check_folder_structure(self, root: str, report: HealthReport) -> None:
        if not os.path.isdir(root):
            report.folder_structure_ok = False
            report.folder_structure_issues.append(f"Dataset root not found: {root}")
            return

        for split in self.REQUIRED_DIRS:
            split_path = os.path.join(root, split)
            if not os.path.isdir(split_path):
                report.folder_structure_ok = False
                report.folder_structure_issues.append(f"Missing split directory: {split}")
                continue

            for sub in self.REQUIRED_SUBDIRS:
                sub_path = os.path.join(split_path, sub)
                if not os.path.isdir(sub_path):
                    report.folder_structure_ok = False
                    report.folder_structure_issues.append(
                        f"Missing subdirectory: {split}/{sub}"
                    )

    def _check_annotation_integrity(self, root: str, report: HealthReport) -> None:
        image_count = 0
        label_count = 0

        for split in self.REQUIRED_DIRS:
            img_dir = os.path.join(root, split, "images")
            lbl_dir = os.path.join(root, split, "labels")

            if not os.path.isdir(img_dir) or not os.path.isdir(lbl_dir):
                continue

            images = set()
            if os.path.isdir(img_dir):
                for fname in os.listdir(img_dir):
                    base = os.path.splitext(fname)[0]
                    images.add(base)
                image_count += len(images)

            labels = set()
            if os.path.isdir(lbl_dir):
                for fname in os.listdir(lbl_dir):
                    base = os.path.splitext(fname)[0]
                    labels.add(base)
                label_count += len(labels)

            missing_labels = images - labels
            orphaned_labels = labels - images
            if missing_labels:
                report.annotation_integrity_ok = False
                report.annotation_integrity_issues.append(
                    f"{split}: {len(missing_labels)} images without labels"
                )
            if orphaned_labels:
                report.annotation_integrity_ok = False
                report.annotation_integrity_issues.append(
                    f"{split}: {len(orphaned_labels)} labels without images"
                )

        report.total_images = image_count
        report.total_labels = label_count

    def _check_image_integrity(self, root: str, report: HealthReport) -> None:
        for split in self.REQUIRED_DIRS:
            img_dir = os.path.join(root, split, "images")
            if not os.path.isdir(img_dir):
                continue

            for fname in os.listdir(img_dir):
                path = os.path.join(img_dir, fname)
                if not os.path.isfile(path):
                    continue
                try:
                    img = cv2.imread(path)
                    if img is None:
                        report.image_integrity_ok = False
                        report.image_integrity_issues.append(
                            f"Corrupted image: {split}/images/{fname}"
                        )
                except Exception:
                    report.image_integrity_ok = False
                    report.image_integrity_issues.append(
                        f"Failed to read: {split}/images/{fname}"
                    )

    def _check_export_integrity(
        self, export_dir: Optional[str], report: HealthReport
    ) -> None:
        if export_dir is None:
            report.export_integrity_ok = True
            return

        if not os.path.isdir(export_dir):
            report.export_integrity_ok = False
            report.export_integrity_issues.append(f"Export directory not found: {export_dir}")
            return

        required_exports = [
            "dataset_quality.json",
            "dataset_health.json",
            "dataset_dashboard.md",
        ]
        for fname in required_exports:
            path = os.path.join(export_dir, fname)
            if not os.path.isfile(path):
                report.export_integrity_ok = False
                report.export_integrity_issues.append(f"Missing export: {fname}")
