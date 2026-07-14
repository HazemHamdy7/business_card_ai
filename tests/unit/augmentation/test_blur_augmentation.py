import numpy as np
import pytest

from src.augmentation.blur_augmentation import BlurAugmentation


class TestBlurAugmentation:
    def make_image(self):
        return np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

    def test_disabled_returns_original(self):
        aug = BlurAugmentation({"enabled": False})
        img = self.make_image()
        result = aug.apply(img)
        assert np.array_equal(img, result)

    def test_applies_blur(self):
        aug = BlurAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_deterministic_seed(self):
        aug = BlurAugmentation({"enabled": True, "probability": 1.0})
        img = self.make_image()
        r1 = aug.apply(img, seed=100)
        r2 = aug.apply(img, seed=100)
        assert np.array_equal(r1, r2)

    def test_gaussian_blur_reduces_sharpness(self):
        aug = BlurAugmentation({"enabled": True, "probability": 1.0})
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        result = aug.apply(img, seed=42)
        original_std = img.std()
        blurred_std = result.std()
        assert blurred_std <= original_std * 1.1

    def test_grayscale(self):
        aug = BlurAugmentation({"enabled": True, "probability": 1.0})
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result = aug.apply(img, seed=42)
        assert result.shape == img.shape
