from __future__ import annotations

import math
import random
from typing import Optional, Tuple

import cv2
import numpy as np


class BlurAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.gaussian_kernel_range: Tuple[int, int] = tuple(
            config.get("gaussian_kernel_range", [3, 7])
        )
        self.motion_blur_kernel_range: Tuple[int, int] = tuple(
            config.get("motion_blur_kernel_range", [5, 15])
        )
        self.probability: float = config.get("probability", 0.3)

    def apply(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if not self.enabled:
            return image
        if seed is not None:
            random.seed(seed)
        if random.random() > self.probability:
            return image

        if seed is not None:
            random.seed(seed + 5)

        if random.random() < 0.5:
            return self._apply_gaussian_blur(image, seed)
        else:
            return self._apply_motion_blur(image, seed)

    def _apply_gaussian_blur(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            random.seed(seed + 6)
        k = random.randint(self.gaussian_kernel_range[0], self.gaussian_kernel_range[1])
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(image, (k, k), 0)

    def _apply_motion_blur(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            random.seed(seed + 7)
        k = random.randint(self.motion_blur_kernel_range[0], self.motion_blur_kernel_range[1])
        if k % 2 == 0:
            k += 1
        angle = random.uniform(0, 180)

        kernel = np.zeros((k, k), dtype=np.float32)
        center = k // 2
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        for i in range(k):
            x = int(round(center + (i - center) * cos_a))
            y = int(round(center + (i - center) * sin_a))
            if 0 <= x < k and 0 <= y < k:
                kernel[y, x] = 1.0
        kernel_sum = kernel.sum()
        if kernel_sum > 0:
            kernel /= kernel_sum
        return cv2.filter2D(image, -1, kernel)
