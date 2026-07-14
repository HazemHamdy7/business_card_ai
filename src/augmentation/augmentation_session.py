from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import cv2
import numpy as np

from .augmentation_config import AugmentationConfig
from .augmentation_pipeline import AugmentationPipeline, PipelineResult


@dataclass
class SessionStats:
    total_images: int = 0
    total_augmented: int = 0
    total_skipped: int = 0
    total_failures: int = 0
    total_time: float = 0.0
    avg_time_per_image: float = 0.0
    transform_counts: Dict[str, int] = field(default_factory=dict)


class AugmentationSession:
    def __init__(self, pipeline: AugmentationPipeline, output_dir: str):
        self.pipeline = pipeline
        self.output_dir = output_dir
        self.stats = SessionStats()
        self.results: List[PipelineResult] = []
        self._start_time: Optional[float] = None

    def process_image(
        self,
        image_path: str,
        output_filename: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Optional[PipelineResult]:
        self.stats.total_images += 1

        image = self._load_image(image_path)
        if image is None:
            self.stats.total_failures += 1
            return None

        result = self.pipeline.process(image, seed=seed)

        if result.applied_transforms:
            self.stats.total_augmented += 1
            for t in result.applied_transforms:
                self.stats.transform_counts[t] = self.stats.transform_counts.get(t, 0) + 1

            if output_filename is None:
                basename = os.path.splitext(os.path.basename(image_path))[0]
                ext = ".jpg"
                output_filename = f"{basename}_augmented{ext}"

            output_path = os.path.join(self.output_dir, output_filename)
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            self._save_image(output_path, result.image)
        else:
            self.stats.total_skipped += 1

        self.results.append(result)
        return result

    def process_batch(
        self,
        image_paths: List[str],
        seed: Optional[int] = None,
    ) -> List[Optional[PipelineResult]]:
        self._start_time = time.perf_counter()
        results = []
        for i, path in enumerate(image_paths):
            batch_seed = None
            if seed is not None:
                batch_seed = seed + i
            result = self.process_image(path, seed=batch_seed)
            results.append(result)
        self.stats.total_time = time.perf_counter() - self._start_time
        if self.stats.total_images > 0:
            self.stats.avg_time_per_image = self.stats.total_time / self.stats.total_images
        return results

    def get_statistics(self) -> SessionStats:
        return self.stats

    def _load_image(self, path: str) -> Optional[np.ndarray]:
        try:
            image = cv2.imread(path)
            if image is None:
                return None
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception:
            return None

    def _save_image(self, path: str, image: np.ndarray) -> None:
        save_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(path, save_image)
