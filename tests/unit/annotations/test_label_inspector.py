import os
import tempfile
import pytest

from src.annotations.label_inspector import LabelInspector


class TestLabelInspector:
    def setup_label(self, label_dir, name, lines):
        path = os.path.join(label_dir, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
        return path

    def setup_image(self, image_dir, name):
        path = os.path.join(image_dir, name)
        with open(path, "w") as f:
            f.write("fake-image-content")
        return path

    def test_inspect_no_label_dir(self):
        result = LabelInspector().inspect("/nonexistent")
        assert result.issues_found
        assert result.total_labels == 0

    def test_inspect_valid_labels(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "img2.txt", ["1 0.2 0.3 0.1 0.2"])
            result = LabelInspector().inspect(label_dir)
            assert result.total_labels == 2
            assert result.valid_labels == 2
            assert not result.issues_found

    def test_inspect_empty_label(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "empty.txt", [])
            result = LabelInspector().inspect(label_dir)
            assert result.total_labels == 1
            assert len(result.empty_labels) == 1
            assert result.issues_found

    def test_inspect_missing_labels(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            result = LabelInspector().inspect(label_dir, image_dir=img_dir)
            assert result.total_images == 2
            assert result.total_labels == 1
            assert len(result.missing_labels) == 1
            assert "img2" in result.missing_labels[0]
            assert result.issues_found

    def test_inspect_orphaned_labels(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "orphan.txt", ["1 0.2 0.3 0.1 0.2"])
            self.setup_image(img_dir, "img1.jpg")
            result = LabelInspector().inspect(label_dir, image_dir=img_dir)
            assert len(result.orphaned_labels) == 1
            assert "orphan" in result.orphaned_labels[0]
            assert result.issues_found

    def test_inspect_no_missing_no_orphans(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "img2.txt", ["1 0.2 0.3 0.1 0.2"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            result = LabelInspector().inspect(label_dir, image_dir=img_dir)
            assert len(result.missing_labels) == 0
            assert len(result.orphaned_labels) == 0
            assert not result.issues_found

    def test_inspect_invalid_class_ids(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "bad.txt", ["9999 0.5 0.5 0.3 0.4"])
            result = LabelInspector().inspect(label_dir)
            assert result.issues_found
            assert "bad.txt" in result.invalid_class_ids

    def test_inspect_out_of_bounds_detected(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "oob.txt", ["0 1.5 0.5 0.3 0.4"])
            result = LabelInspector().inspect(label_dir)
            assert result.issues_found
            assert "oob.txt" in result.out_of_bounds_files

    def test_inspect_out_of_bounds_negative(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "neg.txt", ["0 0.5 -0.5 0.3 0.4"])
            result = LabelInspector().inspect(label_dir)
            assert result.issues_found
            assert "neg.txt" in result.out_of_bounds_files

    def test_inspect_zero_width_height(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "zero.txt", ["0 0.5 0.5 0.0 0.4"])
            result = LabelInspector().inspect(label_dir)
            assert result.issues_found
            assert "zero.txt" in result.out_of_bounds_files

    def test_inspect_custom_allowed_classes(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "bad_class.txt", ["5 0.5 0.5 0.3 0.4"])
            result = LabelInspector(allowed_classes=[0, 1, 2]).inspect(label_dir)
            assert result.issues_found

    def test_inspect_non_txt_files_ignored(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "readme.md", ["# ignore"])
            result = LabelInspector().inspect(label_dir)
            assert result.total_labels == 0

    def test_inspect_image_dir_none(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            result = LabelInspector().inspect(label_dir, image_dir=None)
            assert result.total_images == 0
            assert len(result.missing_labels) == 0
            assert len(result.orphaned_labels) == 0
