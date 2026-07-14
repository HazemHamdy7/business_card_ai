import os
import tempfile
import pytest

from src.annotations.dataset_consistency_checker import DatasetConsistencyChecker


class TestDatasetConsistencyChecker:
    def setup_label(self, label_dir, name, lines):
        path = os.path.join(label_dir, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")

    def setup_image(self, image_dir, name):
        path = os.path.join(image_dir, name)
        with open(path, "w") as f:
            f.write("fake-image-content")

    def test_consistent_dataset(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "img2.txt", ["1 0.2 0.3 0.4 0.2"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            result = DatasetConsistencyChecker().check(label_dir, img_dir)
            assert result.is_consistent
            assert result.total_images == 2
            assert result.total_labels == 2
            assert result.paired == 2
            assert len(result.issues) == 0

    def test_missing_label_dir(self):
        with tempfile.TemporaryDirectory() as img_dir:
            result = DatasetConsistencyChecker().check("/nonexistent", img_dir)
            assert not result.is_consistent
            assert "not found" in result.issues[0]

    def test_missing_image_dir(self):
        with tempfile.TemporaryDirectory() as label_dir:
            result = DatasetConsistencyChecker().check(label_dir, "/nonexistent")
            assert not result.is_consistent
            assert "not found" in result.issues[0]

    def test_unmatched_images(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            self.setup_image(img_dir, "img3.jpg")
            result = DatasetConsistencyChecker().check(label_dir, img_dir)
            assert not result.is_consistent
            assert len(result.unmatched_images) == 2
            assert "without labels" in result.issues[0]

    def test_unmatched_labels(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "orphan.txt", ["1 0.2 0.3 0.4 0.2"])
            self.setup_image(img_dir, "img1.jpg")
            result = DatasetConsistencyChecker().check(label_dir, img_dir)
            assert not result.is_consistent
            assert len(result.unmatched_labels) == 1
            assert "without images" in result.issues[0]

    def test_class_distribution(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4", "1 0.2 0.3 0.1 0.2"])
            self.setup_label(label_dir, "img2.txt", ["0 0.3 0.4 0.2 0.3"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            result = DatasetConsistencyChecker().check(label_dir, img_dir)
            assert result.class_distribution == {0: 2, 1: 1}

    def test_class_distribution_all_paired(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "orphan.txt", ["2 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            result = DatasetConsistencyChecker().check(label_dir, img_dir)
            assert result.class_distribution == {0: 1}

    def test_custom_image_extensions(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.webp")
            result = DatasetConsistencyChecker().check(
                label_dir, img_dir, image_extensions={".webp"}
            )
            assert result.is_consistent
            assert result.paired == 1

    def test_class_names_included(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            result = DatasetConsistencyChecker().check(
                label_dir, img_dir, class_names={0: "business_card"}
            )
            assert result.class_names == {0: "business_card"}

    def test_empty_directories(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            result = DatasetConsistencyChecker().check(label_dir, img_dir)
            assert result.is_consistent
            assert result.total_images == 0
            assert result.total_labels == 0
            assert result.paired == 0
