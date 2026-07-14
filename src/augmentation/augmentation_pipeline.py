from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .augmentation_config import AugmentationConfig
from .blur_augmentation import BlurAugmentation
from .color_augmentation import ColorAugmentation
from .contrast_augmentation import ContrastAugmentation
from .lighting_augmentation import LightingAugmentation
from .noise_augmentation import NoiseAugmentation
from .perspective_augmentation import PerspectiveAugmentation
from .rotation_augmentation import RotationAugmentation


@dataclass
class PipelineResult:
    image: np.ndarray
    applied_transforms: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    original_shape: Tuple[int, ...] = (0,)
    final_shape: Tuple[int, ...] = (0,)


class AugmentationPipeline:
    def __init__(self, config: Optional[AugmentationConfig] = None):
        self.config = config or AugmentationConfig()
        self.seed = self.config.seed
        self._rng_state = None

        self.augmentations = {
            "rotation": RotationAugmentation(self.config.rotation),
            "perspective": PerspectiveAugmentation(self.config.perspective),
            "lighting": LightingAugmentation(self.config.lighting),
            "contrast": ContrastAugmentation(self.config.contrast),
            "blur": BlurAugmentation(self.config.blur),
            "noise": NoiseAugmentation(self.config.noise),
            "color": ColorAugmentation(self.config.color),
        }

        self._order = list(self.augmentations.keys())

    def process(self, image: np.ndarray, seed: Optional[int] = None) -> PipelineResult:
        start = time.perf_counter()
        result_image = image.copy()
        applied: List[str] = []
        use_seed = seed if seed is not None else self.seed

        for i, name in enumerate(self._order):
            aug = self.augmentations[name]
            if not aug.enabled:
                continue
            aug_seed = None
            if use_seed is not None:
                self._rng_state = random.getstate()
                random.seed(use_seed + i)
                aug_seed = use_seed + i
            before = result_image.copy()
            result_image = aug.apply(result_image, seed=aug_seed)
            if not np.array_equal(before, result_image):
                applied.append(name)
            if use_seed is not None:
                random.setstate(self._rng_state)

        elapsed = time.perf_counter() - start

        return PipelineResult(
            image=result_image,
            applied_transforms=applied,
            processing_time=elapsed,
            original_shape=image.shape,
            final_shape=result_image.shape,
        )

    def set_order(self, order: List[str]) -> None:
        valid = set(self.augmentations.keys())
        filtered = [name for name in order if name in valid]
        remaining = [name for name in self._order if name not in filtered]
        self._order = filtered + remaining

    def disable(self, name: str) -> None:
        if name in self.augmentations:
            self.augmentations[name].enabled = False
            if hasattr(self.config, name):
                getattr(self.config, name)["enabled"] = False

    def enable(self, name: str) -> None:
        if name in self.augmentations:
            self.augmentations[name].enabled = True
            if hasattr(self.config, name):
                getattr(self.config, name)["enabled"] = True

    @property
    def enabled_count(self) -> int:
        return sum(1 for aug in self.augmentations.values() if aug.enabled)
