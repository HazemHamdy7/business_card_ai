from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


DEFAULT_QUALITY_CONFIG = {
    "min_resolution": [300, 300],
    "max_resolution": [4096, 4096],
    "min_aspect_ratio": 0.5,
    "max_aspect_ratio": 3.0,
    "allowed_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
    "weights": {
        "label_completeness": 25,
        "image_integrity": 25,
        "format_compliance": 15,
        "resolution_compliance": 20,
        "aspect_ratio_compliance": 15,
    },
}


@dataclass
class QualityResult:
    overall_score: float = 0.0
    label_completeness: float = 0.0
    image_integrity: float = 0.0
    format_compliance: float = 0.0
    resolution_compliance: float = 0.0
    aspect_ratio_compliance: float = 0.0
    missing_labels: List[str] = field(default_factory=list)
    empty_labels: List[str] = field(default_factory=list)
    invalid_labels: List[str] = field(default_factory=list)
    corrupted_images: List[str] = field(default_factory=list)
    unsupported_formats: List[str] = field(default_factory=list)
    resolution_issues: List[str] = field(default_factory=list)
    aspect_ratio_issues: List[str] = field(default_factory=list)
    total_images: int = 0
    total_labels: int = 0
    total_valid: int = 0


class DatasetQuality:
    def __init__(self, config: Optional[dict] = None):
        self.config = {**DEFAULT_QUALITY_CONFIG, **(config or {})}

    def evaluate(
        self,
        image_dir: str,
        label_dir: Optional[str] = None,
    ) -> QualityResult:
        result = QualityResult()
        images = self._collect_images(image_dir)
        result.total_images = len(images)

        label_completeness, missing, empty, invalid = self._evaluate_labels(
            images, label_dir or image_dir
        )
        result.label_completeness = label_completeness
        result.missing_labels = missing
        result.empty_labels = empty
        result.invalid_labels = invalid

        image_integrity, corrupted = self._evaluate_image_integrity(images, image_dir)
        result.image_integrity = image_integrity
        result.corrupted_images = corrupted

        format_compliance, unsupported = self._evaluate_formats(images)
        result.format_compliance = format_compliance
        result.unsupported_formats = unsupported

        resolution_compliance, res_issues = self._evaluate_resolutions(images, image_dir)
        result.resolution_compliance = resolution_compliance
        result.resolution_issues = res_issues

        ar_compliance, ar_issues = self._evaluate_aspect_ratios(images, image_dir)
        result.aspect_ratio_compliance = ar_compliance
        result.aspect_ratio_issues = ar_issues

        result.total_valid = result.total_images - len(result.corrupted_images)
        result.total_labels = result.total_images - len(result.missing_labels)

        weights = self.config["weights"]
        result.overall_score = (
            result.label_completeness * weights["label_completeness"]
            + result.image_integrity * weights["image_integrity"]
            + result.format_compliance * weights["format_compliance"]
            + result.resolution_compliance * weights["resolution_compliance"]
            + result.aspect_ratio_compliance * weights["aspect_ratio_compliance"]
        ) / sum(weights.values())

        return result

    def _collect_images(self, image_dir: str) -> List[str]:
        if not os.path.isdir(image_dir):
            return []
        result = []
        for fname in sorted(os.listdir(image_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".gif"}:
                result.append(fname)
        return result

    def _evaluate_labels(
        self, images: List[str], label_dir: str
    ) -> Tuple[float, List[str], List[str], List[str]]:
        if not images:
            return 100.0, [], [], []
        missing = []
        empty = []
        invalid = []
        valid_count = 0

        for img_name in images:
            base = os.path.splitext(img_name)[0]
            label_path = os.path.join(label_dir, base + ".txt")

            if not os.path.exists(label_path):
                missing.append(base + ".txt")
                continue

            try:
                with open(label_path, "r") as f:
                    lines = f.readlines()
            except Exception:
                invalid.append(base + ".txt")
                continue

            stripped = [l.strip() for l in lines if l.strip()]
            if not stripped:
                empty.append(base + ".txt")
                continue

            all_valid = True
            for line in stripped:
                parts = line.split()
                if len(parts) != 5:
                    all_valid = False
                    break
                try:
                    cls_id = int(parts[0])
                    vals = [float(p) for p in parts[1:]]
                    if cls_id < 0 or not all(0 <= v <= 1 for v in vals):
                        all_valid = False
                        break
                except (ValueError, TypeError):
                    all_valid = False
                    break

            if not all_valid:
                invalid.append(base + ".txt")
            else:
                valid_count += 1

        total = len(images)
        score = (valid_count / total) * 100.0 if total > 0 else 100.0
        return score, missing, empty, invalid

    def _evaluate_image_integrity(
        self, images: List[str], image_dir: str
    ) -> Tuple[float, List[str]]:
        if not images:
            return 100.0, []
        corrupted = []

        for img_name in images:
            path = os.path.join(image_dir, img_name)
            try:
                img = cv2.imread(path)
                if img is None:
                    corrupted.append(img_name)
            except Exception:
                corrupted.append(img_name)

        total = len(images)
        valid_count = total - len(corrupted)
        score = (valid_count / total) * 100.0 if total > 0 else 100.0
        return score, corrupted

    def _evaluate_formats(self, images: List[str]) -> Tuple[float, List[str]]:
        if not images:
            return 100.0, []
        allowed = set(self.config["allowed_formats"])
        unsupported = []

        for img_name in images:
            ext = os.path.splitext(img_name)[1].lower()
            if ext not in allowed:
                unsupported.append(img_name)

        total = len(images)
        valid_count = total - len(unsupported)
        score = (valid_count / total) * 100.0 if total > 0 else 100.0
        return score, unsupported

    def _evaluate_resolutions(
        self, images: List[str], image_dir: str
    ) -> Tuple[float, List[str]]:
        if not images:
            return 100.0, []
        min_res = self.config["min_resolution"]
        max_res = self.config["max_resolution"]
        issues = []

        for img_name in images:
            path = os.path.join(image_dir, img_name)
            try:
                img = cv2.imread(path)
                if img is None:
                    issues.append(img_name)
                    continue
                h, w = img.shape[:2]
                if w < min_res[0] or h < min_res[1] or w > max_res[0] or h > max_res[1]:
                    issues.append(img_name)
            except Exception:
                issues.append(img_name)

        total = len(images)
        valid_count = total - len(issues)
        score = (valid_count / total) * 100.0 if total > 0 else 100.0
        return score, issues

    def _evaluate_aspect_ratios(
        self, images: List[str], image_dir: str
    ) -> Tuple[float, List[str]]:
        if not images:
            return 100.0, []
        min_ar = self.config["min_aspect_ratio"]
        max_ar = self.config["max_aspect_ratio"]
        issues = []

        for img_name in images:
            path = os.path.join(image_dir, img_name)
            try:
                img = cv2.imread(path)
                if img is None:
                    issues.append(img_name)
                    continue
                h, w = img.shape[:2]
                ar = w / h if h > 0 else 0
                if ar < min_ar or ar > max_ar:
                    issues.append(img_name)
            except Exception:
                issues.append(img_name)

        total = len(images)
        valid_count = total - len(issues)
        score = (valid_count / total) * 100.0 if total > 0 else 100.0
        return score, issues
