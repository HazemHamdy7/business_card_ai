import os
import tempfile
import pytest

from src.annotations.annotation_statistics import AnnotationStatistics


class TestAnnotationStatistics:
    def setup_label(self, label_dir, name, lines):
        path = os.path.join(label_dir, name)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")

    def test_compute_empty_directory(self):
        with tempfile.TemporaryDirectory() as label_dir:
            result = AnnotationStatistics().compute(label_dir)
            assert result.total_files == 0
            assert result.total_objects == 0

    def test_compute_single_file_single_object(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            result = AnnotationStatistics().compute(label_dir)
            assert result.total_files == 1
            assert result.total_objects == 1
            assert result.class_distribution == {0: 1}
            assert result.objects_per_image_stats is not None
            assert result.objects_per_image_stats.min == 1
            assert result.objects_per_image_stats.max == 1

    def test_compute_multiple_files(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4", "1 0.2 0.3 0.1 0.2"])
            self.setup_label(label_dir, "img2.txt", ["0 0.3 0.4 0.2 0.3"])
            self.setup_label(label_dir, "img3.txt", ["2 0.1 0.2 0.05 0.1"])
            result = AnnotationStatistics().compute(label_dir)
            assert result.total_files == 3
            assert result.total_objects == 4
            assert result.class_distribution == {0: 2, 1: 1, 2: 1}

    def test_objects_per_image_stats(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            self.setup_label(label_dir, "img2.txt", ["1 0.2 0.3 0.1 0.2", "0 0.3 0.4 0.2 0.3"])
            self.setup_label(label_dir, "img3.txt", [
                "0 0.1 0.2 0.05 0.1",
                "1 0.3 0.4 0.2 0.3",
                "2 0.5 0.6 0.1 0.2",
            ])
            result = AnnotationStatistics().compute(label_dir)
            o = result.objects_per_image_stats
            assert o.min == 1
            assert o.max == 3
            assert o.mean == 2.0
            assert o.median == 2

    def test_bbox_dimension_stats(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", [
                "0 0.5 0.5 0.1 0.2",
                "1 0.3 0.4 0.3 0.4",
            ])
            result = AnnotationStatistics().compute(label_dir)
            w = result.bbox_width_stats
            h = result.bbox_height_stats
            assert w is not None
            assert h is not None
            assert w.min == 0.1
            assert w.max == 0.3
            assert h.min == 0.2
            assert h.max == 0.4

    def test_bbox_area_stats(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", [
                "0 0.5 0.5 0.5 0.5",
                "1 0.3 0.4 0.2 0.2",
            ])
            result = AnnotationStatistics().compute(label_dir)
            a = result.bbox_area_stats
            assert a is not None
            assert a.min == 0.04
            assert a.max == 0.25

    def test_aspect_ratio_buckets(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", [
                "0 0.5 0.5 0.95 0.05",
                "1 0.5 0.5 0.7 0.4",
                "2 0.5 0.5 0.3 0.3",
                "3 0.5 0.5 0.2 0.5",
                "4 0.5 0.5 0.04 0.95",
            ])
            result = AnnotationStatistics().compute(label_dir)
            assert result.aspect_ratio_buckets["ultra_wide"] >= 1
            assert result.aspect_ratio_buckets["wide"] >= 1
            assert result.aspect_ratio_buckets["square"] >= 1
            assert result.aspect_ratio_buckets["tall"] >= 1
            assert result.aspect_ratio_buckets["ultra_tall"] >= 1

    def test_nonexistent_directory(self):
        result = AnnotationStatistics().compute("/nonexistent")
        assert result.total_files == 0
        assert result.total_objects == 0

    def test_only_invalid_labels_skipped(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "bad.txt", ["abc 0.5 0.5 0.3 0.4"])
            result = AnnotationStatistics().compute(label_dir)
            assert result.total_files == 1
            assert result.total_objects == 0

    def test_class_names_included(self):
        with tempfile.TemporaryDirectory() as label_dir:
            self.setup_label(label_dir, "img1.txt", ["0 0.5 0.5 0.3 0.4"])
            result = AnnotationStatistics().compute(
                label_dir, class_names={0: "business_card"}
            )
            assert result.class_names == {0: "business_card"}
