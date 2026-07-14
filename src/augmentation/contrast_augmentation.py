from __future__ import annotations

import random
from typing import Optional, Tuple

import cv2
import numpy as np


class ContrastAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.alpha_range: Tuple[float, float] = tuple(config.get("alpha_range", [0.8, 1.2]))
        self.histogram_equalization: bool = config.get("histogram_equalization", False)
        self.probability: float = config.get("probability", 0.5)

    def apply(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if not self.enabled:
            return image
        if seed is not None:
            random.seed(seed)
        if random.random() > self.probability:
            return image

        result = image.copy()

        if seed is not None:
            random.seed(seed + 4)

        alpha = random.uniform(*self.alpha_range)
        beta = (1.0 - alpha) * 128.0
        result = cv2.convertScaleAbs(result, alpha=alpha, beta=beta)

        if self.histogram_equalization:
            result = self._apply_histogram_equalization(result)

        return result

    def _apply_histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 2:
            return cv2.equalizeHist(image)
        yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
