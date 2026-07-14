from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .annotation_validator import AnnotationValidator


@dataclass
class AnnotationStatsResult:
    label_dir: str
    total_files: int = 0
    total_objects: int = 0
    objects_per_image_stats: Optional["PerImageStats"] = None
    class_distribution: Dict[int, int] = field(default_factory=dict)
    class_names: Dict[int, str] = field(default_factory=dict)
    bbox_width_stats: Optional["BboxDimensionStats"] = None
    bbox_height_stats: Optional["BboxDimensionStats"] = None
    bbox_area_stats: Optional["BboxDimensionStats"] = None
    aspect_ratio_buckets: Dict[str, int] = field(default_factory=dict)


@dataclass
class PerImageStats:
    min: int = 0
    max: int = 0
    mean: float = 0.0
    median: int = 0
    std: float = 0.0


@dataclass
class BboxDimensionStats:
    min: float = 0.0
    max: float = 0.0
    mean: float = 0.0
    median: float = 0.0
    std: float = 0.0


class AnnotationStatistics:
    def __init__(self, allowed_classes: Optional[List[int]] = None):
        self.validator = AnnotationValidator(allowed_classes=allowed_classes)

    def compute(
        self,
        label_dir: str,
        class_names: Optional[Dict[int, str]] = None,
        image_extensions: Optional[Set[str]] = None,
    ) -> AnnotationStatsResult:
        result = AnnotationStatsResult(
            label_dir=label_dir,
            class_names=class_names or {},
        )

        if not os.path.isdir(label_dir):
            return result

        label_files = sorted([
            f for f in os.listdir(label_dir)
            if os.path.isfile(os.path.join(label_dir, f))
            and f.lower().endswith(".txt")
            and not f.startswith(".")
        ])

        result.total_files = len(label_files)

        objects_per_image: List[int] = []
        class_dist: Dict[int, int] = {}
        widths: List[float] = []
        heights: List[float] = []
        areas: List[float] = []
        aspect_buckets: Dict[str, int] = {
            "ultra_wide": 0, "wide": 0, "square": 0, "tall": 0, "ultra_tall": 0,
        }

        for lf in label_files:
            label_path = os.path.join(label_dir, lf)
            vr = self.validator.validate_file(label_path)
            file_count = 0

            for lr in vr.line_results:
                if lr.is_valid:
                    file_count += 1
                    if lr.class_id is not None:
                        class_dist[lr.class_id] = class_dist.get(lr.class_id, 0) + 1
                    if lr.width is not None:
                        widths.append(lr.width)
                    if lr.height is not None:
                        heights.append(lr.height)
                    if lr.width is not None and lr.height is not None:
                        area = lr.width * lr.height
                        areas.append(area)

                        ratio = lr.width / lr.height if lr.height > 0 else 0
                        if ratio >= 3.0:
                            aspect_buckets["ultra_wide"] += 1
                        elif ratio >= 1.5:
                            aspect_buckets["wide"] += 1
                        elif ratio >= 0.67:
                            aspect_buckets["square"] += 1
                        elif ratio >= 0.33:
                            aspect_buckets["tall"] += 1
                        else:
                            aspect_buckets["ultra_tall"] += 1

            if file_count > 0:
                objects_per_image.append(file_count)

        result.total_objects = sum(objects_per_image)

        if objects_per_image:
            result.objects_per_image_stats = self._compute_per_image_stats(objects_per_image)

        result.class_distribution = dict(sorted(class_dist.items()))

        if widths:
            result.bbox_width_stats = self._compute_bbox_stats(widths)
        if heights:
            result.bbox_height_stats = self._compute_bbox_stats(heights)
        if areas:
            result.bbox_area_stats = self._compute_bbox_stats(areas)

        result.aspect_ratio_buckets = aspect_buckets

        return result

    def _compute_per_image_stats(self, counts: List[int]) -> PerImageStats:
        n = len(counts)
        sorted_counts = sorted(counts)
        mean = sum(counts) / n
        variance = sum((x - mean) ** 2 for x in counts) / n

        return PerImageStats(
            min=sorted_counts[0],
            max=sorted_counts[-1],
            mean=round(mean, 2),
            median=sorted_counts[n // 2] if n % 2 == 1
            else (sorted_counts[n // 2 - 1] + sorted_counts[n // 2]) / 2,
            std=round(math.sqrt(variance), 4),
        )

    def _compute_bbox_stats(self, values: List[float]) -> BboxDimensionStats:
        n = len(values)
        sorted_vals = sorted(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n

        return BboxDimensionStats(
            min=round(sorted_vals[0], 6),
            max=round(sorted_vals[-1], 6),
            mean=round(mean, 6),
            median=round(
                sorted_vals[n // 2] if n % 2 == 1
                else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2,
                6,
            ),
            std=round(math.sqrt(variance), 6),
        )
