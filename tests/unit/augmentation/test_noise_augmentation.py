import numpy as np
import pytest

from src.augmentation.noise_augmentation import NoiseAugmentation


class TestNoiseAugmentation:
    def make_image(self):
        return np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = NoiseAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_applies_noise(self):
        aug = NoiseAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_deterministic_seed(self):
        aug = NoiseAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_gaussian_noise_changes_pixels(self):
        aug = NoiseAugmentation({
            "enabled": True, "probability": 1.0,
            "gaussian_std_range": [0.1, 0.1],
            "salt_pepper_amount_range": [0.0, 0.0],
        })
        img = np.full((50, 50, 3), 128, dtype=np.uint8)
        result = aug.apply(img, seed=42)
        diff = np.abs(result.astype(np.float32) - img.astype(np.float32)).max()
        assert diff > 0

    def test_salt_pepper_noise(self):
        aug = NoiseAugmentation({
            "enabled": True, "probability": 1.0,
            "gaussian_std_range": [0.0, 0.0],
            "salt_pepper_amount_range": [0.5, 0.5],
        })
        img = np.full((50, 50, 3), 128, dtype=np.uint8)
        for seed in range(10):
            result = aug.apply(img, seed=seed)
            if (result != 128).any():
                return
        assert False, "No noise produced in 10 seeds"

    def test_output_in_uint8_range(self):
        aug = NoiseAugmentation({
            "enabled": True, "probability": 1.0,
            "gaussian_std_range": [0.5, 0.5],
        })
        img = np.full((50, 50, 3), 128, dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.min() >= 0
        assert result.max() <= 255
