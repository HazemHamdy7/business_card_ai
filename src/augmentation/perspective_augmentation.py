from __future__ import annotations

import random
from typing import Optional

import cv2
import numpy as np


class PerspectiveAugmentation:
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.strength: float = config.get("strength", 0.05)
        self.probability: float = config.get("probability", 0.5)

    def apply(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        if not self.enabled:
            return image
        if seed is not None:
            random.seed(seed)
        if random.random() > self.probability:
            return image

        return self._apply_perspective(image, seed)

    def _apply_perspective(self, image: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        h, w = image.shape[:2]
        s = self.strength

        src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

        if seed is not None:
            random.seed(seed + 2)

        dx1 = random.uniform(-s, s) * w
        dy1 = random.uniform(-s, s) * h
        dx2 = random.uniform(-s, s) * w
        dy2 = random.uniform(-s, s) * h
        dx3 = random.uniform(-s, s) * w
        dy3 = random.uniform(-s, s) * h
        dx4 = random.uniform(-s, s) * w
        dy4 = random.uniform(-s, s) * h

        dst_pts = np.float32([
            [dx1, dy1],
            [w + dx2, dy2],
            [dx3, h + dy3],
            [w + dx4, h + dy4],
        ])

        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return cv2.warpPerspective(image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
