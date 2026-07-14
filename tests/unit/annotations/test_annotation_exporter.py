import json
import os
import tempfile
import pytest

from src.annotations.annotation_exporter import AnnotationExporter
from src.annotations.annotation_validator import AnnotationValidationResult, LineValidationResult
from src.annotations.label_inspector import LabelInspectionResult
from src.annotations.dataset_consistency_checker import ConsistencyResult
from src.annotations.annotation_statistics import AnnotationStatsResult, PerImageStats, BboxDimensionStats


class TestAnnotationExporter:
    def test_export_validation_to_json(self):
        results = [
            AnnotationValidationResult(
                file_path="/path/to/label.txt",
                is_valid=True,
                total_objects=2,
                valid_objects=2,
                line_results=[
                    LineValidationResult(
                        line_number=1, raw="0 0.5 0.5 0.3 0.4", is_valid=True,
                        class_id=0, x_center=0.5, y_center=0.5, width=0.3, height=0.4,
                    ),
                    LineValidationResult(
                        line_number=2, raw="1 0.2 0.3 0.1 0.2", is_valid=True,
                        class_id=1, x_center=0.2, y_center=0.3, width=0.1, height=0.2,
                    ),
                ],
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "validation.json")
            result_path = AnnotationExporter().export_validation_to_json(results, path)
            assert os.path.exists(result_path)
            with open(result_path) as f:
                data = json.load(f)
            assert data["total_files"] == 1
            assert data["valid_count"] == 1
            assert data["files"][0]["is_valid"]

    def test_export_inspection_to_json(self):
        result = LabelInspectionResult(
            label_dir="/labels",
            image_dir="/images",
            total_labels=5,
            total_images=5,
            valid_labels=3,
            invalid_labels=2,
            issues_found=True,
            missing_labels=["img2", "img3"],
            empty_labels=["empty.txt"],
            orphaned_labels=["orphan.txt"],
            invalid_class_ids={"bad.txt": [5]},
            out_of_bounds_files={"oob.txt": ["x_center out of range"]},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "inspection.json")
            result_path = AnnotationExporter().export_inspection_to_json(result, path)
            assert os.path.exists(result_path)
            with open(result_path) as f:
                data = json.load(f)
            assert data["issues_found"]
            assert len(data["missing_labels"]) == 2

    def test_export_consistency_to_json(self):
        result = ConsistencyResult(
            label_dir="/labels",
            image_dir="/images",
            total_images=10,
            total_labels=8,
            paired=8,
            unmatched_images=["img9", "img10"],
            class_distribution={0: 5, 1: 3},
            issues=["2 image(s) without labels"],
            is_consistent=False,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "consistency.json")
            result_path = AnnotationExporter().export_consistency_to_json(result, path)
            assert os.path.exists(result_path)
            with open(result_path) as f:
                data = json.load(f)
            assert not data["is_consistent"]
            assert data["paired"] == 8

    def test_export_statistics_to_json(self):
        result = AnnotationStatsResult(
            label_dir="/labels",
            total_files=10,
            total_objects=25,
            objects_per_image_stats=PerImageStats(min=1, max=5, mean=2.5, median=2, std=1.2),
            class_distribution={0: 15, 1: 10},
            bbox_width_stats=BboxDimensionStats(min=0.1, max=0.9, mean=0.5, median=0.5, std=0.2),
            bbox_height_stats=BboxDimensionStats(min=0.1, max=0.8, mean=0.4, median=0.4, std=0.15),
            bbox_area_stats=BboxDimensionStats(min=0.01, max=0.72, mean=0.25, median=0.2, std=0.18),
            aspect_ratio_buckets={"ultra_wide": 3, "wide": 5, "square": 10, "tall": 4, "ultra_tall": 3},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "statistics.json")
            result_path = AnnotationExporter().export_statistics_to_json(result, path)
            assert os.path.exists(result_path)
            with open(result_path) as f:
                data = json.load(f)
            assert data["total_objects"] == 25
            assert data["objects_per_image"]["mean"] == 2.5

    def test_export_summary_to_markdown(self):
        stats = AnnotationStatsResult(
            label_dir="/labels",
            total_files=10,
            total_objects=25,
            class_distribution={0: 15, 1: 10},
            class_names={0: "card_front", 1: "card_back"},
            aspect_ratio_buckets={"ultra_wide": 3, "wide": 5, "square": 10, "tall": 4, "ultra_tall": 3},
        )
        consistency = ConsistencyResult(
            label_dir="/labels",
            image_dir="/images",
            is_consistent=False,
            total_images=12,
            total_labels=10,
            paired=10,
            unmatched_images=["img11", "img12"],
            issues=["2 image(s) without labels"],
        )
        content = AnnotationExporter().export_summary_to_markdown(
            stats=stats, consistency=consistency
        )
        assert "Annotation Studio Summary" in content
        assert "25" in content
        assert "card_front" in content
        assert "card_back" in content
        assert "2 image(s) without labels" in content

    def test_export_summary_to_markdown_with_path(self):
        stats = AnnotationStatsResult(label_dir="/labels")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "summary.md")
            result_path = AnnotationExporter().export_summary_to_markdown(
                stats=stats, output_path=path
            )
            assert os.path.exists(result_path)
            with open(result_path) as f:
                content = f.read()
            assert "Annotation Studio Summary" in content

    def test_export_summary_empty(self):
        content = AnnotationExporter().export_summary_to_markdown()
        assert "Annotation Studio Summary" in content
