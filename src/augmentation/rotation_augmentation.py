from __future__ import annotations

import math
import random
from typing import Optional, Tuple

import cv2
import numpy as np


class RotationAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.angle_range: Tuple[float, float] = tuple(config.get("angle_range", [-15, 15]))
        self.fixed_angle: Optional[float] = config.get("fixed_angle")
        self.probability: float = config.get("probability", 0.5)

    def apply(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if not self.enabled:
            return image
        if seed is not None:
            random.seed(seed)
        if random.random() > self.probability:
            return image

        angle = self._get_angle(seed)
        return self._rotate(image, angle)

    def _get_angle(self, seed: Optional[int] = None) -> float:
        if self.fixed_angle is not None:
            return self.fixed_angle
        if seed is not None:
            random.seed(seed + 1)
        return random.uniform(*self.angle_range)

    def _rotate(self, image: np.ndarray, angle: float) -> np.ndarray:
        h, w = image.shape[:2]
        center = (w / 2, h / 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = abs(matrix[0, 0])
        sin = abs(matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        matrix[0, 2] += (new_w / 2) - center[0]
        matrix[1, 2] += (new_h / 2) - center[1]
        return cv2.warpAffine(image, matrix, (new_w, new_h), borderMode=cv2.BORDER_REPLICATE)
