from pathlib import Path

from PIL import Image

from src.dataset.dataset_statistics import DatasetStatistics, _categorize_aspect_ratio


def _create_image(path: Path, size=(640, 480), color=(128, 128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path)


def _create_label(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.writelines(lines)


class TestAspectRatioCategorization:
    def test_16_9(self):
        assert _categorize_aspect_ratio(1920, 1080) == "16:9"

    def test_4_3(self):
        assert _categorize_aspect_ratio(800, 600) == "4:3"

    def test_3_2(self):
        assert _categorize_aspect_ratio(960, 640) == "3:2"

    def test_1_1(self):
        assert _categorize_aspect_ratio(500, 500) == "1:1"

    def test_3_4(self):
        assert _categorize_aspect_ratio(600, 800) == "3:4"

    def test_9_16(self):
        assert _categorize_aspect_ratio(540, 960) == "9:16"

    def test_ultrawide(self):
        assert _categorize_aspect_ratio(3000, 1000) == "ultrawide"

    def test_portrait_ultrawide(self):
        assert _categorize_aspect_ratio(200, 1000) == "portrait_ultrawide"

    def test_unknown_height_zero(self):
        assert _categorize_aspect_ratio(100, 0) == "unknown"


class TestDatasetStatistics:
    def test_compute_empty(self, tmp_path):
        root = tmp_path / "dataset"
        root.mkdir()
        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["images"]["total"] == 0
        assert result["dataset_size_bytes"] == 0
        assert result["average_resolution"]["width"] == 0

    def test_compute_with_data(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(1920, 1080))
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        _create_image(root / "raw" / "val" / "images" / "BCA001_002_V1-0.jpg", size=(800, 600))
        _create_label(root / "raw" / "val" / "labels" / "BCA001_002_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["images"]["total"] == 2
        assert result["labels"]["total"] == 2
        assert result["labels"]["total_annotations"] == 2
        assert result["dataset_size_bytes"] > 0
        assert result["dataset_size_mb"] > 0

    def test_image_counts_per_split(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_image(root / "raw" / "val" / "images" / "BCA002_001_V1-0.jpg")
        _create_image(root / "raw" / "test" / "images" / "BCA003_001_V1-0.jpg")

        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["images"]["per_split"]["train"] == 1
        assert result["images"]["per_split"]["val"] == 1
        assert result["images"]["per_split"]["test"] == 1

    def test_average_resolution(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(1920, 1080))
        _create_image(root / "raw" / "train" / "images" / "BCA001_002_V1-0.jpg", size=(640, 480))

        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["average_resolution"]["width"] == 1280
        assert result["average_resolution"]["height"] == 780

    def test_resolution_range(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(640, 480))
        _create_image(root / "raw" / "train" / "images" / "BCA001_002_V1-0.jpg", size=(1920, 1080))

        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["resolution_range"]["width"]["min"] == 640
        assert result["resolution_range"]["width"]["max"] == 1920
        assert result["resolution_range"]["height"]["min"] == 480
        assert result["resolution_range"]["height"]["max"] == 1080

    def test_aspect_ratio_distribution(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(1920, 1080))
        _create_image(root / "raw" / "train" / "images" / "BCA001_002_V1-0.jpg", size=(800, 600))
        _create_image(root / "raw" / "train" / "images" / "BCA001_003_V1-0.jpg", size=(500, 500))

        stats = DatasetStatistics(root)
        result = stats.compute()
        dist = result["aspect_ratio_distribution"]
        assert dist.get("16:9", 0) == 1
        assert dist.get("4:3", 0) == 1
        assert dist.get("1:1", 0) == 1

    def test_dataset_size(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(640, 480))
        _create_image(root / "raw" / "val" / "images" / "BCA001_002_V1-0.jpg", size=(640, 480))

        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["dataset_size_bytes"] > 0
        assert result["per_split"]["train"]["total_size_bytes"] > 0
        assert result["per_split"]["val"]["total_size_bytes"] > 0

    def test_custom_splits(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_image(root / "raw" / "custom" / "images" / "BCA001_002_V1-0.jpg")

        stats = DatasetStatistics(root)
        result = stats.compute(splits=["train", "custom"])
        assert result["images"]["total"] == 2
        assert "custom" in result["images"]["per_split"]

    def test_label_count_mismatch(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_image(root / "raw" / "train" / "images" / "BCA001_002_V1-0.jpg")
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])

        stats = DatasetStatistics(root)
        result = stats.compute()
        assert result["images"]["per_split"]["train"] == 2
        assert result["labels"]["per_split"]["train"] == 1
