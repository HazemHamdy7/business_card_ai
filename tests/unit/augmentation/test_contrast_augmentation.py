import numpy as np
import pytest

from src.augmentation.contrast_augmentation import ContrastAugmentation


class TestContrastAugmentation:
    def make_image(self):
        return np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = ContrastAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_applies_contrast(self):
        aug = ContrastAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_deterministic_seed(self):
        aug = ContrastAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_histogram_equalization(self):
        aug = ContrastAugmentation({
            "enabled": True, "probability": 1.0,
            "alpha_range": [1.0, 1.0],
            "histogram_equalization": True,
        })
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape

    def test_grayscale_histogram_equalization(self):
        aug = ContrastAugmentation({
            "enabled": True, "probability": 1.0,
            "alpha_range": [1.0, 1.0],
            "histogram_equalization": True,
        })
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape

    def test_output_in_uint8_range(self):
        aug = ContrastAugmentation({
            "enabled": True, "probability": 1.0,
            "alpha_range": [3.0, 3.0],
        })
        img = np.full((10, 10, 3), 100, dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.max() <= 255
        assert result.min() >= 0
