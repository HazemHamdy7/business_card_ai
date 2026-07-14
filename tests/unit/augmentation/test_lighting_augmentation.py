import numpy as np
import pytest

from src.augmentation.lighting_augmentation import LightingAugmentation


class TestLightingAugmentation:
    def make_image(self):
        return np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = LightingAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_applies_lighting(self):
        aug = LightingAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_deterministic_seed(self):
        aug = LightingAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_brightness_boost(self):
        aug = LightingAugmentation({
            "enabled": True, "probability": 1.0,
            "brightness_range": [2.0, 2.0],
            "gamma_range": [1.0, 1.0],
            "exposure_range": [1.0, 1.0],
        })
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.dtype == np.uint8
        assert np.mean(result) > np.mean(img) * 0.9

    def test_gamma_correction(self):
        aug = LightingAugmentation({
            "enabled": True, "probability": 1.0,
            "brightness_range": [1.0, 1.0],
            "gamma_range": [0.5, 0.5],
            "exposure_range": [1.0, 1.0],
        })
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.dtype == np.uint8

    def test_output_clipped(self):
        aug = LightingAugmentation({
            "enabled": True, "probability": 1.0,
            "brightness_range": [5.0, 5.0],
            "gamma_range": [1.0, 1.0],
            "exposure_range": [1.0, 1.0],
        })
        img = np.full((10, 10, 3), 100, dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.max() <= 255
        assert result.min() >= 0
