import os
import tempfile

import cv2
import numpy as np
import pytest

from src.dataset.dataset_quality import DatasetQuality
from src.dataset.dataset_health import DatasetHealth
from src.dataset.duplicate_detector import DuplicateDetector


class TestDatasetStress:
    @classmethod
    def setup_class(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.img_dir = cls.tmp.name
        for i in range(500):
            img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
            path = os.path.join(cls.img_dir, f"img{i}.jpg")
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    @classmethod
    def teardown_class(cls):
        cls.tmp.cleanup()

    def test_large_dataset_quality(self):
        q = DatasetQuality()
        result = q.evaluate(self.img_dir)
        assert result.total_images == 500
        assert result.total_valid == 500

    def test_large_dataset_duplicates(self):
        d = DuplicateDetector()
        report = d.find_duplicates(self.img_dir)
        assert report.total_images_checked == 500

    def test_large_dataset_health(self):
        with tempfile.TemporaryDirectory() as root:
            for split in ["train", "val", "test"]:
                for sub in ["images", "labels"]:
                    os.makedirs(os.path.join(root, split, sub), exist_ok=True)
            for i in range(200):
                img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
                path = os.path.join(root, "train", "images", f"img{i}.jpg")
                cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                with open(os.path.join(root, "train", "labels", f"img{i}.txt"), "w") as f:
                    f.write("0 0.5 0.5 0.3 0.4\n")

            h = DatasetHealth()
            report = h.analyze(root)
            assert report.folder_structure_ok
            assert report.annotation_integrity_ok

    def test_with_corrupted_mixed(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(100):
                img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
                path = os.path.join(tmp, f"img{i}.jpg")
                cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            bad_path = os.path.join(tmp, "bad.jpg")
            with open(bad_path, "w") as f:
                f.write("corrupted")

            q = DatasetQuality()
            result = q.evaluate(tmp)
            assert result.total_images == 101
            assert len(result.corrupted_images) == 1
