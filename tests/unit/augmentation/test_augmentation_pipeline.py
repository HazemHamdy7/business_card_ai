import numpy as np
import pytest
import tempfile
import os

from src.augmentation.augmentation_config import AugmentationConfig
from src.augmentation.augmentation_pipeline import AugmentationPipeline


class TestAugmentationPipeline:
    def make_image(self):
        return np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

    def test_process_returns_result(self):
        pipeline = AugmentationPipeline()
        img = self.make_image()
        result = pipeline.process(img, seed=42)
        assert result.image is not None
        assert result.image.shape == img.shape
        assert result.image.dtype == np.uint8
        assert result.processing_time >= 0

    def test_deterministic_seed(self):
        pipeline = AugmentationPipeline(AugmentationConfig(seed=42))
        img = self.make_image()
        r1 = pipeline.process(img)
        r2 = pipeline.process(img)
        assert np.array_equal(r1.image, r2.image)

    def test_all_disabled(self):
        config = AugmentationConfig()
        config.disable_all()
        pipeline = AugmentationPipeline(config)
        img = self.make_image()
        result = pipeline.process(img, seed=42)
        assert np.array_equal(img, result.image)
        assert len(result.applied_transforms) == 0

    def test_tracks_applied_transforms(self):
        config = AugmentationConfig()
        config.enable_all()
        pipeline = AugmentationPipeline(config)
        img = self.make_image()
        result = pipeline.process(img, seed=42)
        assert len(result.applied_transforms) >= 0

    def test_enabled_count(self):
        config = AugmentationConfig()
        pipeline = AugmentationPipeline(config)
        assert pipeline.enabled_count == 7
        pipeline.disable("rotation")
        assert pipeline.enabled_count == 6
        pipeline.disable("blur")
        assert pipeline.enabled_count == 5

    def test_set_order(self):
        config = AugmentationConfig()
        pipeline = AugmentationPipeline(config)
        pipeline.set_order(["rotation", "blur"])
        assert pipeline._order[0] == "rotation"
        assert pipeline._order[1] == "blur"

    def test_disable_enable(self):
        pipeline = AugmentationPipeline()
        pipeline.disable("rotation")
        assert not pipeline.augmentations["rotation"].enabled
        assert not pipeline.config.rotation["enabled"]
        pipeline.enable("rotation")
        assert pipeline.augmentations["rotation"].enabled

    def test_metadata_shape(self):
        pipeline = AugmentationPipeline()
        img = self.make_image()
        result = pipeline.process(img, seed=42)
        assert result.original_shape == (100, 200, 3)
        assert result.final_shape == (100, 200, 3)

    def test_disables_unknown_augmentation_silently(self):
        pipeline = AugmentationPipeline()
        pipeline.disable("unknown")
        pipeline.enable("unknown")

    def test_default_order(self):
        pipeline = AugmentationPipeline()
        assert pipeline._order == [
            "rotation", "perspective", "lighting", "contrast",
            "blur", "noise", "color",
        ]
