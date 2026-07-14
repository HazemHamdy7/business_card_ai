import json
import os
import tempfile
import pytest

from src.annotations.annotation_manager import AnnotationManager


class TestAnnotationManager:
    def setup_label(self, label_dir, name, lines):
        path = os.path.join(label_dir, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")

    def setup_image(self, image_dir, name):
        path = os.path.join(image_dir, name)
        with open(path, "w") as f:
            f.write("fake-image-content")

    def test_run_basic(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "img2.txt", ["1 0.2 0.3 0.1 0.2"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            report = AnnotationManager().run(label_dir, image_dir=img_dir)
            assert report.total_valid_files == 2
            assert report.total_invalid_files == 0
            assert report.total_objects == 2
            assert report.statistics is not None
            assert report.inspection is not None
            assert report.consistency is not None
            assert not report.issues_found

    def test_run_with_invalid_files(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "good.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "bad.txt", ["abc 0.5 0.5 0.3 0.4"])
            report = AnnotationManager().run(label_dir)
            assert report.total_valid_files == 1
            assert report.total_invalid_files == 1
            assert report.issues_found

    def test_run_with_export(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir, tempfile.TemporaryDirectory() as export_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            report = AnnotationManager().run(
                label_dir, image_dir=img_dir, export_dir=export_dir
            )
            assert len(report.export_paths) == 5
            assert os.path.exists(report.export_paths["validation"])
            assert os.path.exists(report.export_paths["inspection"])
            assert os.path.exists(report.export_paths["consistency"])
            assert os.path.exists(report.export_paths["statistics"])
            assert os.path.exists(report.export_paths["summary"])

    def test_run_with_allowed_classes(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "good.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "bad.txt", ["5 0.5 0.5 0.3 0.4"])
            report = AnnotationManager(allowed_classes=[0, 1, 2]).run(label_dir)
            assert report.total_valid_files == 1
            assert report.total_invalid_files == 1

    def test_run_empty_label_dir(self):
        with tempfile.TemporaryDirectory() as label_dir:
            report = AnnotationManager().run(label_dir)
            assert report.total_valid_files == 0
            assert report.total_invalid_files == 0
            assert report.total_objects == 0
            assert not report.issues_found

    def test_run_nonexistent_label_dir(self):
        report = AnnotationManager().run("/nonexistent")
        assert report.total_valid_files == 0
        assert report.total_invalid_files == 0

    def test_run_with_issues_found(self):
        with tempfile.TemporaryDirectory() as label_dir, tempfile.TemporaryDirectory() as img_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            report = AnnotationManager().run(label_dir, image_dir=img_dir)
            assert report.issues_found
            assert len(report.consistency.unmatched_images) == 1

    def test_run_generated_at_timestamp(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            report = AnnotationManager().run(label_dir)
            assert report.generated_at

    def test_run_validated_files_list(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            report = AnnotationManager().run(label_dir)
            assert len(report.validated_files) == 1
            assert report.validated_files[0].is_valid
