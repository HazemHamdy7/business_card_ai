import os
import tempfile

import cv2
import numpy as np
import pytest

from src.augmentation.augmentation_config import AugmentationConfig
from src.augmentation.augmentation_pipeline import AugmentationPipeline
from src.augmentation.augmentation_session import AugmentationSession


class TestAugmentationSession:
    def make_image_file(self, directory, name="test.jpg"):
        img = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        path = os.path.join(directory, name)
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return path

    def test_process_image_success(self):
        with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
            img_path = self.make_image_file(input_dir)
            config = AugmentationConfig()
            config.enable_all()
            pipeline = AugmentationPipeline(config)
            session = AugmentationSession(pipeline, output_dir)

            result = session.process_image(img_path, seed=42)
            assert result is not None
            assert result.image is not None
            assert session.stats.total_images == 1

            files = os.listdir(output_dir)
            assert len(files) > 0

    def test_process_image_nonexistent(self):
        with tempfile.TemporaryDirectory() as output_dir:
            pipeline = AugmentationPipeline()
            session = AugmentationSession(pipeline, output_dir)
            result = session.process_image("nonexistent.jpg", seed=42)
            assert result is None
            assert session.stats.total_failures == 1

    def test_process_batch(self):
        with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
            paths = []
            for i in range(5):
                paths.append(self.make_image_file(input_dir, f"img{i}.jpg"))

            pipeline = AugmentationPipeline()
            session = AugmentationSession(pipeline, output_dir)
            results = session.process_batch(paths, seed=42)
            assert len(results) == 5
            assert all(r is not None for r in results)
            assert session.stats.total_images == 5

    def test_get_statistics(self):
        with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
            path = self.make_image_file(input_dir)

            pipeline = AugmentationPipeline()
            session = AugmentationSession(pipeline, output_dir)
            session.process_image(path, seed=42)
            stats = session.get_statistics()
            assert stats.total_images == 1
            assert stats.total_time >= 0

    def test_statistics_tracking(self):
        with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
            paths = []
            for i in range(3):
                paths.append(self.make_image_file(input_dir, f"img{i}.jpg"))

            pipeline = AugmentationPipeline()
            session = AugmentationSession(pipeline, output_dir)
            session.process_batch(paths, seed=42)
            stats = session.get_statistics()
            assert stats.total_images == 3
            assert stats.total_time > 0
            assert stats.avg_time_per_image > 0

    def test_output_filename_custom(self):
        with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
            path = self.make_image_file(input_dir, "custom.jpg")

            pipeline = AugmentationPipeline()
            session = AugmentationSession(pipeline, output_dir)
            session.process_image(path, output_filename="out.jpg", seed=42)
            assert os.path.exists(os.path.join(output_dir, "out.jpg"))
