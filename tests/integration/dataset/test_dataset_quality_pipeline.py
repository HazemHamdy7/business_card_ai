import json
import os
import tempfile

import cv2
import numpy as np
import pytest

from src.dataset.dataset_quality import DatasetQuality
from src.dataset.dataset_health import DatasetHealth
from src.dataset.dataset_balance import DatasetBalance
from src.dataset.dataset_readiness import DatasetReadiness
from src.dataset.duplicate_detector import DuplicateDetector
from src.dataset.quality_dashboard import QualityDashboard


class TestDatasetQualityPipeline:
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

    def test_full_pipeline_from_scratch(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as export:
            self.make_dataset_structure(root)
            train_img = os.path.join(root, "train", "images")
            train_lbl = os.path.join(root, "train", "labels")
            val_img = os.path.join(root, "val", "images")
            val_lbl = os.path.join(root, "val", "labels")
            test_img = os.path.join(root, "test", "images")
            test_lbl = os.path.join(root, "test", "labels")

            for i in range(20):
                self.make_image(train_img, f"img{i}.jpg")
                self.make_label(train_lbl, f"img{i}.txt")
            for i in range(5):
                self.make_image(val_img, f"img{i}.jpg")
                self.make_label(val_lbl, f"img{i}.txt")
            for i in range(5):
                self.make_image(test_img, f"img{i}.jpg")
                self.make_label(test_lbl, f"img{i}.txt")

            quality = DatasetQuality()
            quality_result = quality.evaluate(
                image_dir=train_img,
                label_dir=train_lbl,
            )
            assert quality_result.overall_score == 100.0
            assert quality_result.total_images == 20

            balance = DatasetBalance(class_names={0: "card_front"})
            balance_result = balance.analyze(
                train_dir=train_lbl,
                val_dir=val_lbl,
                test_dir=test_lbl,
            )
            assert balance_result.total_objects == 30
            assert balance_result.total_images == 30

            duplicates = DuplicateDetector()
            dup_result = duplicates.find_duplicates(train_img)
            assert dup_result.total_exact_duplicate_pairs == 0

            dashboard = QualityDashboard()
            readiness = DatasetReadiness(min_images_per_class=5)
            readiness_result = readiness.evaluate(
                dataset_root=root,
                train_label_dir=train_lbl,
                val_label_dir=val_lbl,
                test_label_dir=test_lbl,
                image_dir=train_img,
            )
            assert readiness_result.is_ready

            json_path = dashboard.generate_json(readiness_result, export)
            md_path = dashboard.generate_markdown(readiness_result, export)

            assert os.path.exists(json_path)
            assert os.path.exists(md_path)

            with open(json_path, "r") as f:
                data = json.load(f)
            assert data["readiness"]["status"] == "READY"

            health = DatasetHealth()
            health_result = health.analyze(root, export_dir=export)
            assert health_result.is_healthy

    def test_pipeline_with_issues(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as export:
            self.make_dataset_structure(root)
            train_img = os.path.join(root, "train", "images")
            train_lbl = os.path.join(root, "train", "labels")

            self.make_image(train_img, "good.jpg")
            bad_path = os.path.join(train_img, "bad.jpg")
            with open(bad_path, "w") as f:
                f.write("corrupted")

            self.make_label(train_lbl, "good.txt")

            readiness = DatasetReadiness().evaluate(
                dataset_root=root,
                train_label_dir=train_lbl,
                image_dir=train_img,
                export_dir=export,
            )
            assert not readiness.is_ready
            assert len(readiness.blocking_issues) > 0

    def test_duplicate_detection_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            pixels = np.full((100, 100, 3), 128, dtype=np.uint8)
            for i in range(3):
                path = os.path.join(tmp, f"dup{i}.jpg")
                cv2.imwrite(path, cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR))
            self.make_image(tmp, "unique.jpg")

            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_exact_duplicate_pairs >= 1
            assert report.total_images_checked == 4
