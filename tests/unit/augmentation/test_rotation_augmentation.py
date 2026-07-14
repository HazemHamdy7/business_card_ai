import numpy as np
import pytest

from src.augmentation.rotation_augmentation import RotationAugmentation


class TestRotationAugmentation:
    def make_image(self, h=100, w=200):
        return np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = RotationAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_enabled_by_default(self):
        aug = RotationAugmentation({})
        assert aug.enabled

    def test_fixed_angle(self):
        aug = RotationAugmentation({"enabled": True, "fixed_angle": 45, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape[0] > 0
        assert result.shape[1] > 0
        assert result.dtype == np.uint8

    def test_random_angle(self):
        aug = RotationAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=42)
        r2 = aug.apply(img, seed=43)
        assert not np.array_equal(r1, r2)

    def test_deterministic_seed(self):
        aug = RotationAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_probability_skip(self):
        aug = RotationAugmentation({"enabled": True, "probability": 0.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert np.array_equal(img, result)

    def test_preserves_image_type(self):
        aug = RotationAugmentation({"enabled": True, "probability": 1.0, "angle_range": [-10, 10]})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.dtype == np.uint8

    def test_grayscale_image(self):
        aug = RotationAugmentation({"enabled": True, "probability": 1.0, "fixed_angle": 30})
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.dtype == np.uint8
        assert len(result.shape) == 2
