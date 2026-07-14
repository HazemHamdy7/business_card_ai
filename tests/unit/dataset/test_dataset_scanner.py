import hashlib
from pathlib import Path

from PIL import Image

from src.dataset.dataset_scanner import DatasetScanner


def _create_image(path: Path, size=(640, 480), color=(128, 128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path)


def _create_label(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.writelines(lines)


def _compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestDatasetScanner:
    def test_scan_empty_dataset(self, tmp_path):
        root = tmp_path / "dataset"
        root.mkdir()
        scanner = DatasetScanner(root)
        result = scanner.scan()
        summary = result["summary"]
        assert summary["total_images"] == 0
        assert summary["total_labels"] == 0
        assert summary["total_missing_images"] == 0
        assert summary["total_missing_labels"] == 0
        assert summary["total_duplicate_groups"] == 0
        assert summary["total_unsupported"] == 0

    def test_scan_complete_dataset(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        for split, offset in [("train", 0), ("val", 3)]:
            for i in range(1, 4):
                stem = f"BCA001_00{i + offset}_V1-0"
                _create_image(root / "raw" / split / "images" / f"{stem}.jpg", color=(i * 50, i * 50, i * 50))
                _create_label(root / "raw" / split / "labels" / f"{stem}.txt", ["0 0.5 0.5 0.4 0.5\n"])

        result = scanner.scan(splits=["train", "val"])
        summary = result["summary"]
        assert summary["total_images"] == 6
        assert summary["total_labels"] == 6
        assert summary["total_missing_images"] == 0
        assert summary["total_missing_labels"] == 0
        assert summary["total_duplicate_groups"] == 0
        assert summary["total_unsupported"] == 0

    def test_scan_missing_labels(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_image(root / "raw" / "train" / "images" / "BCA001_002_V1-0.jpg")
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        result = scanner.scan(splits=["train"])
        assert len(result["missing_labels"]) == 1
        assert result["missing_labels"][0]["stem"] == "BCA001_002_V1-0"
        assert result["summary"]["total_missing_labels"] == 1
        assert result["summary"]["total_missing_images"] == 0

    def test_scan_missing_images(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        _create_label(root / "raw" / "train" / "labels" / "BCA001_002_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        result = scanner.scan(splits=["train"])
        assert len(result["missing_images"]) == 1
        assert result["missing_images"][0]["stem"] == "BCA001_002_V1-0"
        assert result["summary"]["total_missing_images"] == 1
        assert result["summary"]["total_missing_labels"] == 0

    def test_scan_duplicates(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        img_dir = root / "raw" / "train" / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        img_data = Image.new("RGB", (640, 480), (128, 128, 128))
        img_data.save(img_dir / "BCA001_001_V1-0.jpg")
        img_data.save(img_dir / "BCA001_002_V1-0.jpg")

        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        _create_label(root / "raw" / "train" / "labels" / "BCA001_002_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        result = scanner.scan(splits=["train"])
        assert result["summary"]["total_duplicate_groups"] >= 1
        for dup in result["duplicates"]:
            assert len(dup["files"]) > 1

    def test_scan_unsupported_formats(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        img_dir = root / "raw" / "train" / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        (img_dir / "BCA001_001_V1-0.gif").write_text("fake gif content")
        (img_dir / "BCA001_002_V1-0.bmp").write_text("fake bmp")
        (img_dir / "BCA001_003_V1-0.jpg").write_text("fake jpg")

        result = scanner.scan(splits=["train"])
        assert result["summary"]["total_unsupported"] == 1
        assert result["unsupported"][0]["extension"] == ".gif"

    def test_scan_multiple_splits(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        for idx, split in enumerate(["train", "val", "test"], 1):
            stem = f"BCA00{idx}_001_V1-0"
            _create_image(root / "raw" / split / "images" / f"{stem}.jpg", color=(idx * 50, idx * 50, idx * 50))
            _create_label(root / "raw" / split / "labels" / f"{stem}.txt", ["0 0.5 0.5 0.4 0.5\n"])

        result = scanner.scan()
        assert result["summary"]["total_images"] == 3
        assert result["summary"]["total_labels"] == 3

    def test_scan_default_splits(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)

        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        _create_image(root / "raw" / "custom" / "images" / "BCA001_002_V1-0.jpg", color=(200, 200, 200))
        _create_label(root / "raw" / "custom" / "labels" / "BCA001_002_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        result = scanner.scan()
        assert result["summary"]["total_images"] == 1
        assert result["summary"]["total_labels"] == 1

        result_all = scanner.scan(splits=["train", "custom"])
        assert result_all["summary"]["total_images"] == 2

    def test_scan_no_labels_dir(self, tmp_path):
        root = tmp_path / "dataset"
        scanner = DatasetScanner(root)
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")

        result = scanner.scan(splits=["train"])
        assert result["summary"]["total_images"] == 1
        assert result["summary"]["total_labels"] == 0
        assert result["summary"]["total_missing_labels"] == 1
