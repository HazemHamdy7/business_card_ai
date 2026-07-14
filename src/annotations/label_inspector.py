from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .annotation_validator import AnnotationValidator


@dataclass
class LabelInspectionResult:
    label_dir: str
    image_dir: Optional[str] = None
    total_labels: int = 0
    total_images: int = 0
    missing_labels: List[str] = field(default_factory=list)
    orphaned_labels: List[str] = field(default_factory=list)
    empty_labels: List[str] = field(default_factory=list)
    invalid_class_ids: Dict[str, List[int]] = field(default_factory=dict)
    out_of_bounds_files: Dict[str, List[str]] = field(default_factory=dict)
    valid_labels: int = 0
    invalid_labels: int = 0
    issues_found: bool = False


class LabelInspector:
    def __init__(self, allowed_classes: Optional[List[int]] = None):
        self.validator = AnnotationValidator(allowed_classes=allowed_classes)

    def inspect(
        self,
        label_dir: str,
        image_dir: Optional[str] = None,
        image_extensions: Optional[Set[str]] = None,
    ) -> LabelInspectionResult:
        if image_extensions is None:
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

        result = LabelInspectionResult(label_dir=label_dir, image_dir=image_dir)

        if not os.path.isdir(label_dir):
            result.issues_found = True
            return result

        label_files = self._get_label_files(label_dir)
        result.total_labels = len(label_files)

        label_stems: Set[str] = set()
        for lf in label_files:
            stem = os.path.splitext(lf)[0]
            label_stems.add(stem)

            vr = self.validator.validate_file(os.path.join(label_dir, lf))
            if vr.is_empty:
                result.empty_labels.append(lf)
                result.issues_found = True

            if not vr.is_valid and not vr.is_empty:
                result.invalid_labels += 1
                result.issues_found = True
            elif vr.is_valid:
                result.valid_labels += 1

            for lr in vr.line_results:
                if lr.class_id is not None:
                    is_invalid = (
                        lr.class_id < self.validator.MIN_CLASS_ID
                        or lr.class_id > self.validator.MAX_CLASS_ID
                    )
                    if self.validator.allowed_classes is not None:
                        is_invalid = is_invalid or lr.class_id not in self.validator.allowed_classes
                    if is_invalid:
                        result.issues_found = True
                        if lf not in result.invalid_class_ids:
                            result.invalid_class_ids[lf] = []
                        if lr.class_id not in result.invalid_class_ids[lf]:
                            result.invalid_class_ids[lf].append(lr.class_id)

            oob_errors = []
            for lr in vr.line_results:
                if not lr.is_valid:
                    for err in lr.errors:
                        if "out of range" in err.lower() or "must be positive" in err.lower():
                            oob_errors.append(err)
            if oob_errors:
                result.issues_found = True
                result.out_of_bounds_files[lf] = oob_errors

        if image_dir and os.path.isdir(image_dir):
            image_files = [
                f for f in os.listdir(image_dir)
                if os.path.isfile(os.path.join(image_dir, f))
                and os.path.splitext(f)[1].lower() in image_extensions
            ]
            result.total_images = len(image_files)
            image_stems: Set[str] = {os.path.splitext(f)[0] for f in image_files}

            missing = image_stems - label_stems
            result.missing_labels = sorted(missing)
            if result.missing_labels:
                result.issues_found = True

            orphaned = label_stems - image_stems
            result.orphaned_labels = sorted(orphaned)
            if result.orphaned_labels:
                result.issues_found = True

        return result

    def _get_label_files(self, label_dir: str) -> List[str]:
        return sorted([
            f for f in os.listdir(label_dir)
            if os.path.isfile(os.path.join(label_dir, f))
            and f.lower().endswith(".txt")
            and not f.startswith(".")
        ])
