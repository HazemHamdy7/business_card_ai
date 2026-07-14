from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class BalanceReport:
    objects_per_class: Dict[str, int] = field(default_factory=dict)
    images_per_class: Dict[str, int] = field(default_factory=dict)
    split_distribution: Dict[str, int] = field(default_factory=dict)
    imbalance_score: float = 0.0
    total_objects: int = 0
    total_images: int = 0
    num_classes: int = 0
    class_names: Dict[int, str] = field(default_factory=dict)


class DatasetBalance:
    def __init__(self, class_names: Optional[Dict[int, str]] = None):
        self.class_names = class_names or {}

    def analyze(
        self,
        train_dir: Optional[str] = None,
        val_dir: Optional[str] = None,
        test_dir: Optional[str] = None,
    ) -> BalanceReport:
        report = BalanceReport(class_names=self.class_names)
        splits = {"train": train_dir, "val": val_dir, "test": test_dir}

        for split_name, split_path in splits.items():
            if split_path is None or not os.path.isdir(split_path):
                continue
            count = self._count_labels(split_path)
            report.split_distribution[split_name] = count

        all_objects: Dict[str, int] = {}
        all_images: Dict[str, int] = {}
        total_objects = 0
        total_images = 0

        for split_name, split_path in splits.items():
            if split_path is None or not os.path.isdir(split_path):
                continue
            obj_counts, img_counts = self._analyze_split(split_path)
            for cls_name, count in obj_counts.items():
                all_objects[cls_name] = all_objects.get(cls_name, 0) + count
                total_objects += count
            for cls_name, count in img_counts.items():
                all_images[cls_name] = all_images.get(cls_name, 0) + count
                total_images += count

        report.objects_per_class = dict(sorted(all_objects.items()))
        report.images_per_class = dict(sorted(all_images.items()))
        report.total_objects = total_objects
        report.total_images = total_images
        report.num_classes = max(len(all_objects), 1)

        report.imbalance_score = self._compute_imbalance(all_objects)

        return report

    def _count_labels(self, label_dir: str) -> int:
        count = 0
        if not os.path.isdir(label_dir):
            return 0
        for fname in os.listdir(label_dir):
            if fname.endswith(".txt"):
                count += 1
        return count

    def _analyze_split(
        self, label_dir: str
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        objects: Dict[str, int] = {}
        images: Dict[str, int] = {}

        if not os.path.isdir(label_dir):
            return objects, images

        for fname in os.listdir(label_dir):
            if not fname.endswith(".txt"):
                continue
            path = os.path.join(label_dir, fname)
            seen_classes = set()
            try:
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) < 1:
                            continue
                        try:
                            cls_id = int(parts[0])
                        except (ValueError, IndexError):
                            continue
                        cls_name = self.class_names.get(cls_id, str(cls_id))
                        objects[cls_name] = objects.get(cls_name, 0) + 1
                        seen_classes.add(cls_name)
            except Exception:
                continue

            for cls_name in seen_classes:
                images[cls_name] = images.get(cls_name, 0) + 1

        return objects, images

    def _compute_imbalance(self, counts: Dict[str, int]) -> float:
        if not counts or len(counts) <= 1:
            return 0.0
        values = list(counts.values())
        max_count = max(values)
        min_count = min(values)
        if max_count == 0:
            return 0.0
        return 1.0 - (min_count / max_count)
