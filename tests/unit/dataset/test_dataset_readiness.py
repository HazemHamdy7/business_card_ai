import os
import tempfile

import cv2
import numpy as np
import pytest

from src.dataset.dataset_readiness import DatasetReadiness
from src.dataset.dataset_quality import DatasetQuality
from src.dataset.dataset_health import DatasetHealth


class TestDatasetReadiness:
    def make_image(self, directory, name="test.jpg", w=640, h=480):
        path = os.path.join(directory, name)
        img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return path

    def make_label(self, directory, name="test.txt", lines=None):
        if lines is None:
            lines = ["0 0.5 0.5 0.3 0.4"]
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
        return path

    def make_dataset_structure(self, root):
        for split in ["train", "val", "test"]:
            for sub in ["images", "labels"]:
                os.makedirs(os.path.join(root, split, sub), exist_ok=True)

    def test_empty_dataset_not_ready(self):
        with tempfile.TemporaryDirectory() as root:
            result = DatasetReadiness().evaluate(dataset_root=root)
            assert result.status == "NOT_READY"
            assert not result.is_ready

    def test_good_dataset_ready(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_dataset_structure(root)
            for i in range(15):
                self.make_image(os.path.join(root, "train", "images"), f"img{i}.jpg")
                self.make_label(os.path.join(root, "train", "labels"), f"img{i}.txt",
                                lines=["0 0.5 0.5 0.3 0.4"])

            result = DatasetReadiness(min_images_per_class=5).evaluate(
                dataset_root=root,
                train_label_dir=os.path.join(root, "train", "labels"),
                image_dir=os.path.join(root, "train", "images"),
            )
            assert result.status == "READY"
            assert result.is_ready

    def test_blocking_issues_reported(self):
        with tempfile.TemporaryDirectory() as root:
            result = DatasetReadiness().evaluate(dataset_root=root)
            assert len(result.blocking_issues) > 0
            assert len(result.recommendations) > 0

    def test_low_quality_not_ready(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as img_dir:
            self.make_dataset_structure(root)
            self.make_image(img_dir, "img1.jpg")

            result = DatasetReadiness(min_quality_score=99.0).evaluate(
                dataset_root=root,
                image_dir=img_dir,
            )
            assert result.status == "NOT_READY"

    def test_corrupted_image_blocks(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as img_dir:
            self.make_dataset_structure(root)
            bad_path = os.path.join(img_dir, "bad.jpg")
            with open(bad_path, "w") as f:
                f.write("not an image")

            result = DatasetReadiness().evaluate(
                dataset_root=root,
                image_dir=img_dir,
            )
            assert result.status == "NOT_READY"

    def test_readiness_properties(self):
        r = DatasetReadiness()
        assert hasattr(r, "MIN_QUALITY_SCORE")
        assert hasattr(r, "MAX_IMBALANCE_SCORE")
        assert hasattr(r, "MIN_IMAGES_PER_CLASS")
