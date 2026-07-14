import os
import tempfile

import pytest

from src.annotations.annotation_manager import AnnotationManager


class TestAnnotationPipeline:
    def setup_labels(self, label_dir):
        with open(os.path.join(label_dir, "img1.txt"), "w") as f:
            f.write("0 0.5 0.5 0.3 0.4\n")
        with open(os.path.join(label_dir, "img2.txt"), "w") as f:
            f.write("1 0.2 0.3 0.1 0.2\n")
        with open(os.path.join(label_dir, "img3.txt"), "w") as f:
            f.write("invalid\n")

    def setup_images(self, image_dir):
        with open(os.path.join(image_dir, "img1.jpg"), "w") as f:
            pass
        with open(os.path.join(image_dir, "img2.jpg"), "w") as f:
            pass
        with open(os.path.join(image_dir, "img3.jpg"), "w") as f:
            pass
        with open(os.path.join(image_dir, "extra.jpg"), "w") as f:
            pass

    def test_full_pipeline_with_export(self):
        with (
            tempfile.TemporaryDirectory() as label_dir,
            tempfile.TemporaryDirectory() as image_dir,
            tempfile.TemporaryDirectory() as export_dir,
        ):
            self.setup_labels(label_dir)
            self.setup_images(image_dir)

            manager = AnnotationManager(allowed_classes=[0, 1])
            report = manager.run(
                label_dir=label_dir,
                image_dir=image_dir,
                export_dir=export_dir,
            )

            assert report.total_valid_files == 2
            assert report.total_invalid_files == 1
            assert report.total_objects == 2
            assert report.issues_found

            assert report.inspection is not None
            assert report.consistency is not None
            assert report.statistics is not None

            assert report.consistency.total_images == 4
            assert report.consistency.total_labels == 3
            assert report.consistency.paired == 3
            assert len(report.consistency.unmatched_images) == 1

            assert report.statistics.total_files == 3
            assert report.statistics.total_objects == 2
            assert report.statistics.class_distribution == {0: 1, 1: 1}

            assert len(report.export_paths) == 5
            for key in ("validation", "inspection", "consistency", "statistics", "summary"):
                assert os.path.exists(report.export_paths[key])

    def test_pipeline_no_images(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_labels(label_dir)

            report = AnnotationManager(allowed_classes=[0, 1]).run(label_dir)

            assert report.total_valid_files == 2
            assert report.total_invalid_files == 1
            assert report.inspection is None
            assert report.consistency is None
            assert report.statistics is not None

    def test_pipeline_invalid_allowed_classes(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_labels(label_dir)

            manager = AnnotationManager(allowed_classes=[0])
            report = manager.run(label_dir)

            assert report.total_valid_files == 1
            assert report.total_invalid_files == 2

    def test_pipeline_empty_label_dir(self):
        with tempfile.TemporaryDirectory() as label_dir:
            report = AnnotationManager().run(label_dir)
            assert report.total_valid_files == 0
            assert report.total_invalid_files == 0
            assert not report.issues_found
            assert report.statistics is not None
            assert report.statistics.total_files == 0

    def test_pipeline_nonexistent_dirs(self):
        report = AnnotationManager().run(
            label_dir=r"C:\nonexistent\labels",
            image_dir=r"C:\nonexistent\images",
        )
        assert report.total_valid_files == 0
        assert report.total_invalid_files == 0
        assert report.inspection is not None
        assert report.consistency is not None
        assert report.statistics is not None
