import numpy as np
import pytest

from src.augmentation.color_augmentation import ColorAugmentation


class TestColorAugmentation:
    def make_image(self):
        return np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = ColorAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_applies_color(self):
        aug = ColorAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_deterministic_seed(self):
        aug = ColorAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_saturation_adjustment(self):
        aug = ColorAugmentation({
            "enabled": True, "probability": 1.0,
            "saturation_range": [0.0, 0.0],
            "hue_range": [0.0, 0.0],
            "white_balance_range": [1.0, 1.0],
        })
        img = self.make_image()
        result = aug.apply(img, seed=42)
        hsv = np.zeros_like(img)
        hsv_result = np.zeros_like(result)
        import cv2
        hsv_orig = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsv_new = cv2.cvtColor(result, cv2.COLOR_RGB2HSV)
        assert hsv_new[:, :, 1].mean() <= hsv_orig[:, :, 1].mean()

    def test_output_in_uint8_range(self):
        aug = ColorAugmentation({
            "enabled": True, "probability": 1.0,
            "saturation_range": [5.0, 5.0],
        })
        img = np.full((10, 10, 3), 128, dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.min() >= 0
        assert result.max() <= 255
