from __future__ import annotations

import math
import random
from typing import Optional, Tuple

import cv2
import numpy as np


class NoiseAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.gaussian_std_range: Tuple[float, float] = tuple(
            config.get("gaussian_std_range", [0.01, 0.03])
        )
        self.salt_pepper_amount_range: Tuple[float, float] = tuple(
            config.get("salt_pepper_amount_range", [0.01, 0.03])
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
            random.seed(seed + 8)

        if random.random() < 0.5:
            return self._apply_gaussian_noise(image, seed)
        else:
            return self._apply_salt_pepper_noise(image, seed)

    def _apply_gaussian_noise(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            random.seed(seed + 9)
            np.random.seed(seed + 9)
        std = random.uniform(*self.gaussian_std_range)
        noise = np.random.normal(0, std * 255, image.shape).astype(np.float32)
        result = image.astype(np.float32) + noise
        return np.clip(result, 0, 255).astype(np.uint8)

    def _apply_salt_pepper_noise(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            random.seed(seed + 10)
            np.random.seed(seed + 10)
        amount = random.uniform(*self.salt_pepper_amount_range)
        salt_vs_pepper = 0.5

        result = image.copy()
        num_pixels = image.size // image.shape[2] if len(image.shape) == 3 else image.size
        num_salt = int(num_pixels * amount * salt_vs_pepper)
        num_pepper = int(num_pixels * amount * (1.0 - salt_vs_pepper))

        coords = [np.random.randint(0, i, num_salt) for i in image.shape[:2]]
        result[coords[0], coords[1]] = 255

        coords = [np.random.randint(0, i, num_pepper) for i in image.shape[:2]]
        result[coords[0], coords[1]] = 0

        return result
