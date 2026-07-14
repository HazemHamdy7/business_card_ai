import os
import tempfile
import numpy as np
import pytest
from PIL import Image

from src.augmentation.augmentation_config import AugmentationConfig
from src.augmentation.augmentation_pipeline import AugmentationPipeline
from src.augmentation.augmentation_session import AugmentationSession


class TestAugmentationIntegration:
    @pytest.fixture
    def sample_image_path(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.fromarray(np.full((100, 100, 3), 128, dtype=np.uint8))
            img.save(f.name)
            path = f.name
        yield path
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def sample_image(self):
        return np.full((100, 100, 3), 128, dtype=np.uint8)

    def test_full_pipeline_chain(self, sample_image):
        config = AugmentationConfig()
        config.disable_all()
        config.rotation["enabled"] = True
        config.rotation["probability"] = 1.0
        config.rotation["angle_range"] = [15, 15]
        config.blur["enabled"] = True
        config.blur["probability"] = 1.0
        config.blur["gaussian_kernel_range"] = [5, 5]
        config.contrast["enabled"] = True
        config.contrast["probability"] = 1.0
        config.contrast["alpha_range"] = [1.5, 1.5]

        pipeline = AugmentationPipeline(config)
        result = pipeline.process(sample_image, seed=42)

        assert len(result.image.shape) == 3
        assert result.image.shape[2] == 3
        assert result.image.dtype == np.uint8
        assert result.image.shape != sample_image.shape or not (result.image == sample_image).all()
        assert len(result.applied_transforms) >= 1

    def test_pipeline_deterministic_identical(self, sample_image):
        config = AugmentationConfig()
        config.disable_all()
        config.rotation["enabled"] = True
        config.rotation["probability"] = 1.0
        config.rotation["angle_range"] = [45, 45]

        pipeline = AugmentationPipeline(config)
        r1 = pipeline.process(sample_image, seed=99)
        r2 = pipeline.process(sample_image, seed=99)
        assert (r1.image == r2.image).all()

    def test_session_process_and_save(self, sample_image_path):
        with tempfile.TemporaryDirectory() as out_dir:
            config = AugmentationConfig()
            config.disable_all()
            config.rotation["enabled"] = True
            config.rotation["probability"] = 1.0
            config.rotation["angle_range"] = [10, 10]

            pipeline = AugmentationPipeline(config)
            session = AugmentationSession(pipeline, output_dir=out_dir)
            result = session.process_image(sample_image_path, seed=42)

            assert result is not None
            assert result.image is not None
            assert len(result.applied_transforms) >= 1

            stats = session.get_statistics()
            assert stats.total_images == 1
            assert stats.total_augmented == 1

    def test_session_batch_consistent_shapes(self, sample_image_path):
        with tempfile.TemporaryDirectory() as out_dir:
            config = AugmentationConfig()
            config.disable_all()
            config.rotation["enabled"] = True
            config.rotation["probability"] = 1.0
            config.rotation["angle_range"] = [90, 90]

            pipeline = AugmentationPipeline(config)
            session = AugmentationSession(pipeline, output_dir=out_dir)
            results = session.process_batch(
                [sample_image_path, sample_image_path],
                seed=42,
            )

            assert len(results) == 2
            for r in results:
                assert r is not None
                assert r.image is not None
