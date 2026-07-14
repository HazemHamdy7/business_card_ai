from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .annotation_validator import AnnotationValidator


@dataclass
class ConsistencyResult:
    label_dir: str
    image_dir: str
    total_images: int = 0
    total_labels: int = 0
    paired: int = 0
    unmatched_images: List[str] = field(default_factory=list)
    unmatched_labels: List[str] = field(default_factory=list)
    class_distribution: Dict[int, int] = field(default_factory=dict)
    class_names: Dict[int, str] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    is_consistent: bool = True


class DatasetConsistencyChecker:
    def __init__(self, allowed_classes: Optional[List[int]] = None):
        self.validator = AnnotationValidator(allowed_classes=allowed_classes)

    def check(
        self,
        label_dir: str,
        image_dir: str,
        image_extensions: Optional[Set[str]] = None,
        class_names: Optional[Dict[int, str]] = None,
    ) -> ConsistencyResult:
        if image_extensions is None:
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

        result = ConsistencyResult(
            label_dir=label_dir,
            image_dir=image_dir,
            class_names=class_names or {},
        )

        if not os.path.isdir(label_dir):
            result.issues.append(f"Label directory not found: {label_dir}")
            result.is_consistent = False
            return result

        if not os.path.isdir(image_dir):
            result.issues.append(f"Image directory not found: {image_dir}")
            result.is_consistent = False
            return result

        image_files = [
            f for f in os.listdir(image_dir)
            if os.path.isfile(os.path.join(image_dir, f))
            and os.path.splitext(f)[1].lower() in image_extensions
            and not f.startswith(".")
        ]
        image_stems: Dict[str, str] = {
            os.path.splitext(f)[0]: f for f in image_files
        }
        result.total_images = len(image_files)

        label_files = [
            f for f in os.listdir(label_dir)
            if os.path.isfile(os.path.join(label_dir, f))
            and f.lower().endswith(".txt")
            and not f.startswith(".")
        ]
        label_stems: Dict[str, str] = {
            os.path.splitext(f)[0]: f for f in label_files
        }
        result.total_labels = len(label_files)

        paired_stems = set(image_stems.keys()) & set(label_stems.keys())
        result.paired = len(paired_stems)

        unmatched_image_stems = set(image_stems.keys()) - set(label_stems.keys())
        result.unmatched_images = sorted(
            [image_stems[s] for s in unmatched_image_stems]
        )

        unmatched_label_stems = set(label_stems.keys()) - set(image_stems.keys())
        result.unmatched_labels = sorted(
            [label_stems[s] for s in unmatched_label_stems]
        )

        if result.unmatched_images:
            result.issues.append(
                f"{len(result.unmatched_images)} image(s) without labels"
            )
            result.is_consistent = False

        if result.unmatched_labels:
            result.issues.append(
                f"{len(result.unmatched_labels)} label(s) without images"
            )
            result.is_consistent = False

        class_dist: Dict[int, int] = {}
        for stem in paired_stems:
            label_path = os.path.join(label_dir, label_stems[stem])
            vr = self.validator.validate_file(label_path)
            for lr in vr.line_results:
                if lr.is_valid and lr.class_id is not None:
                    class_dist[lr.class_id] = class_dist.get(lr.class_id, 0) + 1

        result.class_distribution = dict(sorted(class_dist.items()))

        return result
