from pathlib import Path

from PIL import Image

from src.dataset.dataset_validator import DatasetValidator


def _create_image(path: Path, size=(640, 480), color=(128, 128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path)


def _create_label(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.writelines(lines)


def _make_valid_dataset(root: Path, size=(1920, 1080)):
    batches = {"train": "BCA001", "val": "BCA002", "test": "BCA003"}
    for split, batch in batches.items():
        for i in range(1, 4):
            stem = f"{batch}_00{i}_V1-0"
            _create_image(root / "raw" / split / "images" / f"{stem}.jpg", size=size)
            _create_label(root / "raw" / split / "labels" / f"{stem}.txt", ["0 0.5 0.5 0.4 0.5\n"])
    return root


class TestDatasetValidator:
    def test_validate_structure_missing(self, tmp_path):
        root = tmp_path / "dataset"
        root.mkdir()
        validator = DatasetValidator(root)
        issues = validator.validate_structure()
        assert len(issues) == 1
        assert issues[0]["level"] == "error"

    def test_validate_structure_valid(self, tmp_path):
        root = _make_valid_dataset(tmp_path / "dataset")
        validator = DatasetValidator(root)
        issues = validator.validate_structure()
        assert len(issues) == 0

    def test_validate_structure_partial(self, tmp_path):
        root = tmp_path / "dataset"
        (root / "raw" / "train" / "images").mkdir(parents=True)
        validator = DatasetValidator(root)
        issues = validator.validate_structure()
        warning_messages = [i["message"] for i in issues]
        assert any("labels" in m for m in warning_messages)
        assert any("val" in m or "test" in m for m in warning_messages)

    def test_validate_labels_valid(self, tmp_path):
        root = _make_valid_dataset(tmp_path / "dataset")
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert len(issues) == 0

    def test_validate_labels_invalid_format(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["invalid\n"])
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("expected 5 values" in i["message"] for i in issues)

    def test_validate_labels_non_numeric(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["a b c d e\n"])
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("Non-numeric" in i["message"] for i in issues)

    def test_validate_labels_out_of_range_class(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["5 0.5 0.5 0.4 0.5\n"])
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("Class ID 5" in i["message"] for i in issues)

    def test_validate_labels_allowed_class_v2(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["1 0.5 0.5 0.4 0.5\n"])
        validator = DatasetValidator(root, version="V2-0")
        issues = validator.validate_labels("train")
        assert len([i for i in issues if "Class ID" in i["message"]]) == 0

    def test_validate_labels_x_center_out_of_range(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 1.5 0.5 0.4 0.5\n"])
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("x_center" in i["message"] for i in issues)

    def test_validate_labels_width_out_of_range(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0 0.5\n"])
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("width" in i["message"] for i in issues)

    def test_validate_labels_empty_file(self, tmp_path):
        root = tmp_path / "dataset"
        label_path = root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt"
        label_path.parent.mkdir(parents=True)
        label_path.write_text("")
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("Empty label file" in i["message"] for i in issues)

    def test_validate_labels_blank_lines(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["\n", "\n"])
        validator = DatasetValidator(root)
        issues = validator.validate_labels("train")
        assert any("Empty label file" in i["message"] for i in issues)

    def test_validate_images_valid(self, tmp_path):
        root = _make_valid_dataset(tmp_path / "dataset")
        validator = DatasetValidator(root)
        issues = validator.validate_images("train")
        assert len(issues) == 0

    def test_validate_images_too_small(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(100, 100))
        validator = DatasetValidator(root)
        issues = validator.validate_images("train")
        assert any("too small" in i["message"] for i in issues)

    def test_validate_images_too_large(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(5000, 5000))
        validator = DatasetValidator(root)
        issues = validator.validate_images("train")
        assert any("too large" in i["message"] for i in issues)

    def test_validate_images_corrupt(self, tmp_path):
        root = tmp_path / "dataset"
        img_path = root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg"
        img_path.parent.mkdir(parents=True)
        img_path.write_bytes(b"not a valid image file")
        validator = DatasetValidator(root)
        issues = validator.validate_images("train")
        assert any("Cannot open" in i["message"] for i in issues)

    def test_validate_naming_valid(self, tmp_path):
        root = tmp_path / "dataset"
        valid_names = [
            "BCA001_001_V1-0.jpg",
            "BCA999_999_V2-0.png",
            "DRC_BCA001_002_V1-0.png",
            "WEB_BCA001_003_V1-0.jpeg",
        ]
        for name in valid_names:
            _create_image(root / "raw" / "train" / "images" / name)
        validator = DatasetValidator(root)
        issues = validator.validate_naming("train")
        assert len(issues) == 0

    def test_validate_naming_invalid(self, tmp_path):
        root = tmp_path / "dataset"
        invalid_names = [
            "test.png",
            "BCA001_001.jpg",
            "BCA001_001_V1-0_extra.jpg",
        ]
        for name in invalid_names:
            _create_image(root / "raw" / "train" / "images" / name)
        validator = DatasetValidator(root)
        issues = validator.validate_naming("train")
        assert len(issues) == len(invalid_names)

    def test_validate_split_integrity_no_overlap(self, tmp_path):
        root = _make_valid_dataset(tmp_path / "dataset")
        validator = DatasetValidator(root)
        issues = validator.validate_split_integrity(["train", "val", "test"])
        assert len(issues) == 0

    def test_validate_split_integrity_with_overlap(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_image(root / "raw" / "val" / "images" / "BCA001_001_V1-0.jpg")
        validator = DatasetValidator(root)
        issues = validator.validate_split_integrity(["train", "val"])
        assert len(issues) == 1
        assert "multiple splits" in issues[0]["message"]

    def test_validate_all_summary_pass(self, tmp_path):
        root = _make_valid_dataset(tmp_path / "dataset")
        validator = DatasetValidator(root)
        results = validator.validate_all()
        assert results["summary"]["passed"] is True
        assert results["summary"]["total_errors"] == 0

    def test_validate_all_summary_fail(self, tmp_path):
        root = tmp_path / "dataset"
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 1.5 0.5 0.4 0.5\n"])
        validator = DatasetValidator(root)
        results = validator.validate_all()
        assert results["summary"]["passed"] is False
        assert results["summary"]["total_errors"] > 0

    def test_validate_all_with_custom_splits(self, tmp_path):
        root = _make_valid_dataset(tmp_path / "dataset")
        validator = DatasetValidator(root)
        results = validator.validate_all(splits=["train"])
        assert "train" in results["labels"]
        assert "val" not in results["labels"]
