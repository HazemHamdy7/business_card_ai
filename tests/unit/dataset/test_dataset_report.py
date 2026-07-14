import json

from src.dataset.dataset_report import DatasetReport


class TestDatasetReport:
    def test_generate_empty(self):
        report = DatasetReport()
        result = report.generate()
        assert "generated_at" in result
        assert result["scan"] == {}
        assert result["validation"] == {}
        assert result["statistics"] == {}

    def test_to_json(self):
        scanner_data = {"summary": {"total_images": 10, "total_labels": 10}}
        report = DatasetReport(scanner_result=scanner_data)
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["scan"]["summary"]["total_images"] == 10

    def test_to_json_with_path(self, tmp_path):
        output = tmp_path / "report.json"
        report_data = {"summary": {"total_images": 5}}
        report = DatasetReport(scanner_result=report_data)
        json_str = report.to_json(path=output)
        assert output.exists()
        assert output.read_text() == json_str

    def test_to_markdown(self):
        scanner_data = {"summary": {"total_images": 10, "total_labels": 10}}
        report = DatasetReport(scanner_result=scanner_data)
        md = report.to_markdown()
        assert "# Dataset Management Report" in md
        assert "10" in md
        assert "Scanner Results" in md

    def test_to_markdown_with_path(self, tmp_path):
        output = tmp_path / "report.md"
        report = DatasetReport()
        md = report.to_markdown(path=output)
        assert output.exists()
        assert output.read_text() == md

    def test_generate_with_all_data(self):
        scanner = {
            "missing_images": [{"stem": "BCA001_001_V1-0", "split": "train"}],
            "summary": {"total_images": 1, "total_missing_images": 1},
        }
        validator = {
            "structure": [],
            "labels": {"train": []},
            "images": {"train": []},
            "naming": {"train": []},
            "split_integrity": [],
            "summary": {"total_errors": 0, "passed": True},
        }
        stats = {
            "images": {"total": 1, "per_split": {"train": 1}},
            "dataset_size_mb": 1.5,
            "average_resolution": {"width": 640, "height": 480},
        }

        report = DatasetReport(
            scanner_result=scanner,
            validator_result=validator,
            statistics=stats,
        )
        result = report.generate()
        assert result["scan"]["summary"]["total_images"] == 1
        assert result["validation"]["summary"]["passed"] is True
        assert result["statistics"]["images"]["total"] == 1

    def test_markdown_with_issues(self):
        scanner = {
            "missing_images": [{"stem": "BCA001_001_V1-0", "split": "train"}],
            "missing_labels": [],
            "duplicates": [{"hash": "abc123", "files": ["img1.jpg", "img2.jpg"]}],
            "unsupported": [{"path": "test.gif", "extension": ".gif"}],
            "summary": {
                "total_images": 2,
                "total_labels": 1,
                "total_missing_images": 1,
                "total_missing_labels": 0,
                "total_duplicate_groups": 1,
                "total_unsupported": 1,
            },
        }
        report = DatasetReport(scanner_result=scanner)
        md = report.to_markdown()
        assert "Missing Images" in md
        assert "BCA001_001_V1-0" in md
        assert "Duplicate Files" in md
        assert "Unsupported Formats" in md

    def test_markdown_no_issues(self):
        scanner = {
            "missing_images": [],
            "missing_labels": [],
            "duplicates": [],
            "unsupported": [],
            "summary": {"total_images": 1, "total_labels": 1, "total_missing_images": 0, "total_missing_labels": 0, "total_duplicate_groups": 0, "total_unsupported": 0},
        }
        report = DatasetReport(scanner_result=scanner)
        md = report.to_markdown()
        assert "No issues found" in md

    def test_markdown_with_validation_errors(self, tmp_path):
        validator = {
            "structure": [{"level": "warning", "message": "Missing directory: raw/val/images/"}],
            "labels": {
                "train": [{"level": "error", "file": "test.txt", "line": 1, "message": "Invalid format"}]
            },
            "images": {"train": []},
            "naming": {"train": []},
            "split_integrity": [],
            "summary": {"total_errors": 1, "total_warnings": 1, "passed": False},
        }
        report = DatasetReport(validator_result=validator)
        md = report.to_markdown()
        assert "Validation Errors" in md
        assert "Invalid format" in md
        assert "Validation Warnings" in md
        assert "Missing directory" in md
