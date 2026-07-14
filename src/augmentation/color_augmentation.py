from __future__ import annotations

import random
from typing import Optional, Tuple

import cv2
import numpy as np


class ColorAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.saturation_range: Tuple[float, float] = tuple(config.get("saturation_range", [0.8, 1.2]))
        self.hue_range: Tuple[float, float] = tuple(config.get("hue_range", [-10, 10]))
        self.white_balance_range: Tuple[float, float] = tuple(
            config.get("white_balance_range", [0.9, 1.1])
        )
        self.probability: float = config.get("probability", 0.5)

    def apply(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if not self.enabled:
            return image
        if seed is not None:
            random.seed(seed)
        if random.random() > self.probability:
            return image

        result = image.copy().astype(np.float32)

        if seed is not None:
            random.seed(seed + 11)

        saturation = random.uniform(*self.saturation_range)
        hue_shift = random.uniform(*self.hue_range)
        wb_r = random.uniform(*self.white_balance_range)
        wb_g = random.uniform(*self.white_balance_range)
        wb_b = random.uniform(*self.white_balance_range)

        result = self._adjust_saturation_hue(result, saturation, hue_shift)
        result = self._adjust_white_balance(result, wb_r, wb_g, wb_b)

        return np.clip(result, 0, 255).astype(np.uint8)

    def _adjust_saturation_hue(self, image: np.ndarray, saturation: float, hue_shift: float) -> np.ndarray:
        hsv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

    def _adjust_white_balance(self, image: np.ndarray, r: float, g: float, b: float) -> np.ndarray:
        result = image.copy()
        if len(result.shape) == 3 and result.shape[2] >= 3:
            result[:, :, 0] = result[:, :, 0] * r
            result[:, :, 1] = result[:, :, 1] * g
            result[:, :, 2] = result[:, :, 2] * b
        return result
