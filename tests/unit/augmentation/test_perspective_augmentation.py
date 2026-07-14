import numpy as np
import pytest

from src.augmentation.perspective_augmentation import PerspectiveAugmentation


class TestPerspectiveAugmentation:
    def make_image(self, h=100, w=200):
        return np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = PerspectiveAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_enabled_by_default(self):
        aug = PerspectiveAugmentation({})
        assert aug.enabled

    def test_applies_distortion(self):
        aug = PerspectiveAugmentation({"enabled": True, "strength": 0.1, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_deterministic_seed(self):
        aug = PerspectiveAugmentation({"enabled": True, "strength": 0.1, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_low_strength_minimal_change(self):
        aug = PerspectiveAugmentation({"enabled": True, "strength": 0.001, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        diff = np.mean(np.abs(img.astype(np.float32) - result.astype(np.float32)))
        assert diff < 10

    def test_high_strength_changes_image(self):
        aug = PerspectiveAugmentation({"enabled": True, "strength": 0.2, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        diff = np.mean(np.abs(img.astype(np.float32) - result.astype(np.float32)))
        assert diff > 0

    def test_grayscale(self):
        aug = PerspectiveAugmentation({"enabled": True, "strength": 0.1, "probability": 1.0})
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
