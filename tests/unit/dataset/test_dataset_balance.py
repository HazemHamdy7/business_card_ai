import os
import tempfile

import pytest

from src.dataset.dataset_balance import DatasetBalance


class TestDatasetBalance:
    def make_label(self, directory, name="test.txt", lines=None):
        if lines is None:
            lines = ["0 0.5 0.5 0.3 0.4"]
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
        return path

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = DatasetBalance()
            report = b.analyze(train_dir=tmp)
            assert report.total_objects == 0
            assert report.total_images == 0
            assert report.imbalance_score == 0.0

    def test_single_class(self):
        with tempfile.TemporaryDirectory() as lbl:
            for i in range(3):
                self.make_label(lbl, f"img{i}.txt", lines=["0 0.5 0.5 0.3 0.4"])

            b = DatasetBalance()
            report = b.analyze(train_dir=lbl)
            assert report.total_objects == 3
            assert report.total_images == 3
            assert "0" in report.objects_per_class
            assert report.objects_per_class["0"] == 3

    def test_multiple_classes(self):
        with tempfile.TemporaryDirectory() as lbl:
            self.make_label(lbl, "img1.txt", lines=["0 0.5 0.5 0.3 0.4"])
            self.make_label(lbl, "img2.txt", lines=["1 0.5 0.5 0.3 0.4"])
            self.make_label(lbl, "img3.txt", lines=["0 0.5 0.5 0.3 0.4", "1 0.5 0.5 0.3 0.4"])

            b = DatasetBalance()
            report = b.analyze(train_dir=lbl)
            assert report.total_objects == 4
            assert report.num_classes == 2

    def test_class_names(self):
        with tempfile.TemporaryDirectory() as lbl:
            self.make_label(lbl, "img1.txt", lines=["0 0.5 0.5 0.3 0.4"])
            self.make_label(lbl, "img2.txt", lines=["1 0.5 0.5 0.3 0.4"])

            b = DatasetBalance(class_names={0: "card_front", 1: "card_back"})
            report = b.analyze(train_dir=lbl)
            assert "card_front" in report.objects_per_class
            assert "card_back" in report.objects_per_class
            assert report.objects_per_class["card_front"] == 1

    def test_split_distribution(self):
        with tempfile.TemporaryDirectory() as train, tempfile.TemporaryDirectory() as val:
            for i in range(5):
                self.make_label(train, f"img{i}.txt")
            for i in range(2):
                self.make_label(val, f"img{i}.txt")

            b = DatasetBalance()
            report = b.analyze(train_dir=train, val_dir=val)
            assert report.split_distribution["train"] == 5
            assert report.split_distribution["val"] == 2

    def test_imbalance_score(self):
        with tempfile.TemporaryDirectory() as lbl:
            self.make_label(lbl, "img1.txt", lines=["0 0.5 0.5 0.3 0.4"] * 10)
            self.make_label(lbl, "img2.txt", lines=["1 0.5 0.5 0.3 0.4"])

            b = DatasetBalance()
            report = b.analyze(train_dir=lbl)
            assert report.imbalance_score > 0.0

    def test_perfect_balance(self):
        with tempfile.TemporaryDirectory() as lbl:
            for i in range(5):
                self.make_label(lbl, f"img{i}.txt", lines=["0 0.5 0.5 0.3 0.4"])
                self.make_label(lbl, f"img{i}_b.txt", lines=["1 0.5 0.5 0.3 0.4"])

            b = DatasetBalance()
            report = b.analyze(train_dir=lbl)
            assert report.imbalance_score == 0.0

    def test_non_label_files_ignored(self):
        with tempfile.TemporaryDirectory() as lbl:
            self.make_label(lbl, "img1.txt", lines=["0 0.5 0.5 0.3 0.4"])
            with open(os.path.join(lbl, "readme.md"), "w") as f:
                f.write("# notes")

            b = DatasetBalance()
            report = b.analyze(train_dir=lbl)
            assert report.total_objects == 1
