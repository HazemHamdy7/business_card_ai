import json
from pathlib import Path

from PIL import Image

from src.dataset.dataset_exporter import DatasetExporter
from src.dataset.dataset_report import DatasetReport
from src.dataset.dataset_scanner import DatasetScanner
from src.dataset.dataset_statistics import DatasetStatistics
from src.dataset.dataset_validator import DatasetValidator


def _create_image(path: Path, size=(640, 480), color=(128, 128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path)


def _create_label(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.writelines(lines)


class TestDatasetPipeline:
    def test_full_clean_pipeline(self, tmp_path):
        root = tmp_path / "dataset"
        batches = {"train": "BCA001", "val": "BCA002", "test": "BCA003"}
        for split, batch in batches.items():
            for i in range(1, 4):
                stem = f"{batch}_00{i}_V1-0"
                _create_image(root / "raw" / split / "images" / f"{stem}.jpg", size=(1920, 1080))
                _create_label(root / "raw" / split / "labels" / f"{stem}.txt", ["0 0.5 0.5 0.4 0.5\n"])

        scanner = DatasetScanner(root)
        scan_result = scanner.scan()
        assert scan_result["summary"]["total_images"] == 9
        assert scan_result["summary"]["total_missing_images"] == 0
        assert scan_result["summary"]["total_missing_labels"] == 0

        validator = DatasetValidator(root)
        val_result = validator.validate_all()
        assert val_result["summary"]["passed"] is True

        statistics = DatasetStatistics(root)
        stats_result = statistics.compute()
        assert stats_result["images"]["total"] == 9
        assert stats_result["average_resolution"]["width"] == 1920

        report = DatasetReport(
            scanner_result=scan_result,
            validator_result=val_result,
            statistics=stats_result,
        )
        json_report = report.to_json(tmp_path / "report.json")
        md_report = report.to_markdown(tmp_path / "report.md")
        assert (tmp_path / "report.json").exists()
        assert (tmp_path / "report.md").exists()

        exporter = DatasetExporter(root)
        export_dir = tmp_path / "export"
        exporter.export_yolo(export_dir)
        assert (export_dir / "train" / "images").exists()

        with open(tmp_path / "report.json") as f:
            parsed = json.load(f)
            assert parsed["scan"]["summary"]["total_images"] == 9
            assert parsed["validation"]["summary"]["passed"] is True
            assert parsed["statistics"]["images"]["total"] == 9

    def test_pipeline_with_issues(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(640, 480))
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        _create_image(root / "raw" / "train" / "images" / "BCA001_002_V1-0.jpg", size=(640, 480))
        _create_image(root / "raw" / "train" / "images" / "BCA001_003_V1-0.jpg", size=(640, 480))
        _create_image(root / "raw" / "train" / "images" / "bad_file.png", size=(640, 480))
        _create_label(root / "raw" / "train" / "labels" / "BCA001_002_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        (root / "raw" / "train" / "images" / "test.gif").write_text("fake")

        scanner = DatasetScanner(root)
        scan_result = scanner.scan(splits=["train"])
        assert scan_result["summary"]["total_missing_labels"] == 2
        assert scan_result["summary"]["total_unsupported"] == 1

        validator = DatasetValidator(root)
        val_result = validator.validate_all(splits=["train"])
        assert val_result["summary"]["passed"] is False
        naming_issues = val_result["naming"]["train"]
        assert any("bad_file" in i["file"] for i in naming_issues)

        report = DatasetReport(scanner_result=scan_result, validator_result=val_result)
        md = report.to_markdown()
        assert "Missing Labels" in md
        assert "Unsupported Formats" in md
        assert "Validation Errors" in md

    def test_pipeline_with_duplicates_and_exports(self, tmp_path):
        root = tmp_path / "dataset"
        img_dir = root / "raw" / "train" / "images"
        img_dir.mkdir(parents=True)
        label_dir = root / "raw" / "train" / "labels"
        label_dir.mkdir(parents=True)

        img_data = Image.new("RGB", (100, 100), (128, 128, 128))
        img_data.save(img_dir / "BCA001_001_V1-0.jpg")
        img_data.save(img_dir / "BCA001_002_V1-0.jpg")
        _create_label(label_dir / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        _create_label(label_dir / "BCA001_002_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        scanner = DatasetScanner(root)
        scan_result = scanner.scan(splits=["train"])
        assert scan_result["summary"]["total_duplicate_groups"] >= 1

        validator = DatasetValidator(root)
        val_result = validator.validate_all(splits=["train"])
        assert val_result["summary"]["passed"] is False
        img_issues = val_result["images"]["train"]
        assert any("too small" in i["message"] for i in img_issues)

        exporter = DatasetExporter(root)
        export_dir = tmp_path / "yolo_out"
        exporter.export_yolo(export_dir, splits=["train"])
        assert (export_dir / "train" / "images" / "BCA001_001_V1-0.jpg").exists()
