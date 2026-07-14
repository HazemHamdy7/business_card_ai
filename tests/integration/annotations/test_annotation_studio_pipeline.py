import os
import json
import tempfile
import pytest

from src.annotations.annotation_manager import AnnotationManager


class TestAnnotationStudioPipeline:
    def setup_label(self, label_dir, name, lines):
        path = os.path.join(label_dir, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")

    def setup_image(self, image_dir, name):
        path = os.path.join(image_dir, name)
        with open(path, "w") as f:
            f.write("fake-image-content")

    def test_full_annotation_pipeline(self):
        with (tempfile.TemporaryDirectory() as label_dir,
              tempfile.TemporaryDirectory() as img_dir,
              tempfile.TemporaryDirectory() as export_dir):
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "img2.txt", ["1 0.2 0.3 0.1 0.2", "0 0.3 0.4 0.2 0.3"])
            self.setup_label(label_dir, "img3.txt", ["2 0.1 0.2 0.05 0.1"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")
            self.setup_image(img_dir, "img3.jpg")

            report = AnnotationManager(class_names={
                0: "card_front", 1: "card_back", 2: "side_view"
            }).run(
                label_dir=label_dir,
                image_dir=img_dir,
                export_dir=export_dir,
            )

            assert report.total_valid_files == 3
            assert report.total_invalid_files == 0
            assert report.total_objects == 4
            assert report.inspection.total_labels == 3
            assert report.inspection.total_images == 3
            assert not report.inspection.issues_found
            assert report.consistency.is_consistent
            assert report.consistency.paired == 3
            assert report.statistics.class_distribution == {0: 2, 1: 1, 2: 1}
            assert os.path.exists(export_dir)

    def test_pipeline_with_issues(self):
        with (tempfile.TemporaryDirectory() as label_dir,
              tempfile.TemporaryDirectory() as img_dir,
              tempfile.TemporaryDirectory() as export_dir):
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "bad.txt", ["abc 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "empty.txt", [])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "img2.jpg")

            report = AnnotationManager().run(
                label_dir=label_dir,
                image_dir=img_dir,
                export_dir=export_dir,
            )

            assert report.total_valid_files == 1
            assert report.total_invalid_files == 2
            assert report.issues_found
            assert len(report.inspection.empty_labels) == 1
            assert len(report.consistency.unmatched_images) == 1

    def test_pipeline_with_all_export_files(self):
        with (tempfile.TemporaryDirectory() as label_dir,
              tempfile.TemporaryDirectory() as img_dir,
              tempfile.TemporaryDirectory() as export_dir):
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")

            report = AnnotationManager().run(
                label_dir=label_dir,
                image_dir=img_dir,
                export_dir=export_dir,
            )

            for key, path in report.export_paths.items():
                assert os.path.exists(path), f"Export path missing: {key} -> {path}"

            with open(report.export_paths["validation"]) as f:
                data = json.load(f)
                assert data["valid_count"] == 1

            with open(report.export_paths["statistics"]) as f:
                data = json.load(f)
                assert data["total_objects"] == 1

            with open(report.export_paths["summary"]) as f:
                content = f.read()
                assert "Annotation Studio Summary" in content

    def test_pipeline_empty_dataset(self):
        with tempfile.TemporaryDirectory() as label_dir:
            report = AnnotationManager().run(label_dir=label_dir)
            assert report.total_valid_files == 0
            assert report.total_invalid_files == 0
            assert report.total_objects == 0
            assert not report.issues_found

    def test_pipeline_with_rejection(self):
        with (tempfile.TemporaryDirectory() as label_dir,
              tempfile.TemporaryDirectory() as img_dir):
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "oob.txt", ["0 1.5 0.5 0.3 0.4"])
            self.setup_image(img_dir, "img1.jpg")
            self.setup_image(img_dir, "oob.jpg")

            report = AnnotationManager(allowed_classes=[0, 1]).run(
                label_dir=label_dir,
                image_dir=img_dir,
            )

            assert report.total_valid_files == 1
            assert report.total_invalid_files == 1
            assert report.issues_found
            assert "oob.txt" in report.inspection.out_of_bounds_files
