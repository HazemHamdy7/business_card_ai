import os
import tempfile

import cv2
import numpy as np
import pytest

from src.dataset.dataset_quality import DatasetQuality, DEFAULT_QUALITY_CONFIG


class TestDatasetQuality:
    def make_image(self, directory, name="test.jpg", w=640, h=480):
        path = os.path.join(directory, name)
        img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return path

    def make_label(self, directory, name="test.txt", lines=None):
        if lines is None:
            lines = ["0 0.5 0.5 0.3 0.4"]
        path = os.path.join(directory, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
        return path

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            q = DatasetQuality()
            result = q.evaluate(tmp)
            assert result.overall_score == 100.0
            assert result.total_images == 0

    def test_all_valid_images_and_labels(self):
        with tempfile.TemporaryDirectory() as img_dir, tempfile.TemporaryDirectory() as lbl_dir:
            self.make_image(img_dir, "img1.jpg")
            self.make_image(img_dir, "img2.jpg")
            self.make_label(lbl_dir, "img1.txt")
            self.make_label(lbl_dir, "img2.txt")

            q = DatasetQuality()
            result = q.evaluate(img_dir, label_dir=lbl_dir)
            assert result.overall_score == 100.0
            assert result.total_images == 2
            assert result.total_labels == 2
            assert result.total_valid == 2
            assert len(result.missing_labels) == 0

    def test_missing_labels(self):
        with tempfile.TemporaryDirectory() as img_dir, tempfile.TemporaryDirectory() as lbl_dir:
            self.make_image(img_dir, "img1.jpg")
            self.make_image(img_dir, "img2.jpg")
            self.make_label(lbl_dir, "img1.txt")

            q = DatasetQuality()
            result = q.evaluate(img_dir, label_dir=lbl_dir)
            assert result.overall_score < 100.0
            assert len(result.missing_labels) == 1

    def test_empty_labels(self):
        with tempfile.TemporaryDirectory() as img_dir, tempfile.TemporaryDirectory() as lbl_dir:
            self.make_image(img_dir, "img1.jpg")
            self.make_label(lbl_dir, "img1.txt", lines=[])

            q = DatasetQuality()
            result = q.evaluate(img_dir, label_dir=lbl_dir)
            assert len(result.empty_labels) == 1

    def test_invalid_labels(self):
        with tempfile.TemporaryDirectory() as img_dir, tempfile.TemporaryDirectory() as lbl_dir:
            self.make_image(img_dir, "img1.jpg")
            self.make_label(lbl_dir, "img1.txt", lines=["invalid"])

            q = DatasetQuality()
            result = q.evaluate(img_dir, label_dir=lbl_dir)
            assert len(result.invalid_labels) == 1

    def test_corrupted_image(self):
        with tempfile.TemporaryDirectory() as img_dir:
            path = os.path.join(img_dir, "bad.jpg")
            with open(path, "w") as f:
                f.write("not an image")

            q = DatasetQuality()
            result = q.evaluate(img_dir)
            assert len(result.corrupted_images) == 1
            assert result.image_integrity < 100.0

    def test_unsupported_format(self):
        with tempfile.TemporaryDirectory() as img_dir:
            self.make_image(img_dir, "img1.gif")
            q = DatasetQuality(config={"allowed_formats": [".jpg", ".png"]})
            result = q.evaluate(img_dir)
            assert len(result.unsupported_formats) == 1

    def test_resolution_issues(self):
        with tempfile.TemporaryDirectory() as img_dir:
            img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
            path = os.path.join(img_dir, "small.jpg")
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

            q = DatasetQuality()
            result = q.evaluate(img_dir)
            assert len(result.resolution_issues) == 1

    def test_aspect_ratio_issues(self):
        with tempfile.TemporaryDirectory() as img_dir:
            img = np.random.randint(0, 256, (100, 400, 3), dtype=np.uint8)
            path = os.path.join(img_dir, "wide.jpg")
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

            q = DatasetQuality()
            result = q.evaluate(img_dir)
            assert len(result.aspect_ratio_issues) == 1

    def test_custom_config(self):
        config = {**DEFAULT_QUALITY_CONFIG, "min_resolution": [100, 100]}
        q = DatasetQuality(config=config)
        assert q.config["min_resolution"] == [100, 100]
