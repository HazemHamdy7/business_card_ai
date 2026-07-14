import os
import tempfile

import cv2
import numpy as np
import pytest

from src.dataset.dataset_health import DatasetHealth


class TestDatasetHealth:
    def make_dataset_structure(self, root, splits=None):
        if splits is None:
            splits = ["train", "val", "test"]
        for split in splits:
            for sub in ["images", "labels"]:
                os.makedirs(os.path.join(root, split, sub), exist_ok=True)

    def make_image(self, directory, name="test.jpg"):
        path = os.path.join(directory, name)
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return path

    def make_label(self, directory, name="test.txt"):
        path = os.path.join(directory, name)
        with open(path, "w") as f:
            f.write("0 0.5 0.5 0.3 0.4\n")
        return path

    def test_nonexistent_root(self):
        h = DatasetHealth()
        report = h.analyze("/nonexistent/path")
        assert not report.is_healthy
        assert not report.folder_structure_ok

    def test_healthy_dataset(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_dataset_structure(root)
            h = DatasetHealth()
            report = h.analyze(root)
            assert report.folder_structure_ok

    def test_missing_split(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_dataset_structure(root, splits=["train"])
            h = DatasetHealth()
            report = h.analyze(root)
            assert not report.folder_structure_ok
            assert any("val" in issue for issue in report.folder_structure_issues)

    def test_missing_subdir(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "train", "images"), exist_ok=True)
            h = DatasetHealth()
            report = h.analyze(root)
            assert not report.folder_structure_ok

    def test_missing_labels_detected(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_dataset_structure(root)
            self.make_image(os.path.join(root, "train", "images"), "img1.jpg")
            self.make_image(os.path.join(root, "train", "images"), "img2.jpg")
            self.make_label(os.path.join(root, "train", "labels"), "img1.txt")

            h = DatasetHealth()
            report = h.analyze(root)
            assert not report.annotation_integrity_ok
            assert any("without labels" in issue for issue in report.annotation_integrity_issues)

    def test_orphaned_labels_detected(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_dataset_structure(root)
            self.make_label(os.path.join(root, "train", "labels"), "orphan.txt")

            h = DatasetHealth()
            report = h.analyze(root)
            assert not report.annotation_integrity_ok
            assert any("without images" in issue for issue in report.annotation_integrity_issues)

    def test_corrupted_image_detected(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_dataset_structure(root)
            bad_path = os.path.join(root, "train", "images", "bad.jpg")
            with open(bad_path, "w") as f:
                f.write("not an image")

            h = DatasetHealth()
            report = h.analyze(root)
            assert not report.image_integrity_ok
            assert any("Corrupted" in issue for issue in report.image_integrity_issues)

    def test_export_integrity(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as export:
            self.make_dataset_structure(root)
            h = DatasetHealth()
            report = h.analyze(root, export_dir=export)
            assert not report.export_integrity_ok

    def test_export_integrity_all_present(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as export:
            self.make_dataset_structure(root)
            for fname in ["dataset_quality.json", "dataset_health.json", "dataset_dashboard.md"]:
                with open(os.path.join(export, fname), "w") as f:
                    f.write("{}")
            h = DatasetHealth()
            report = h.analyze(root, export_dir=export)
            assert report.export_integrity_ok
