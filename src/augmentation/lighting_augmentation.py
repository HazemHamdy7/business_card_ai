from __future__ import annotations

import random
from typing import Optional, Tuple

import cv2
import numpy as np


class LightingAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.brightness_range: Tuple[float, float] = tuple(config.get("brightness_range", [0.8, 1.2]))
        self.gamma_range: Tuple[float, float] = tuple(config.get("gamma_range", [0.8, 1.2]))
        self.exposure_range: Tuple[float, float] = tuple(config.get("exposure_range", [0.9, 1.1]))
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
            random.seed(seed + 3)

        brightness = random.uniform(*self.brightness_range)
        gamma = random.uniform(*self.gamma_range)
        exposure = random.uniform(*self.exposure_range)

        result = self._adjust_brightness(result, brightness)
        result = self._adjust_gamma(result, gamma)
        result = self._adjust_exposure(result, exposure)

        return np.clip(result, 0, 255).astype(np.uint8)

    def _adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        return image * factor

    def _adjust_gamma(self, image: np.ndarray, gamma: float) -> np.ndarray:
        normalized = image / 255.0
        corrected = np.power(normalized, gamma)
        return corrected * 255.0

    def _adjust_exposure(self, image: np.ndarray, factor: float) -> np.ndarray:
        clipped = np.clip(image, 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(clipped, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
