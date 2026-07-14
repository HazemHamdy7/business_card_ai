import time
from pathlib import Path

import pytest
from PIL import Image

from src.dataset.dataset_scanner import DatasetScanner
from src.dataset.dataset_statistics import DatasetStatistics
from src.dataset.dataset_validator import DatasetValidator

BENCHMARK_IMAGE_COUNT = 50


def _create_image(path: Path, size=(640, 480), color=(128, 128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path)


def _create_label(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("0 0.5 0.5 0.4 0.5\n")


@pytest.fixture(scope="module")
def benchmark_dataset(tmp_path_factory):
    root = tmp_path_factory.mktemp("benchmark_dataset")
    for i in range(BENCHMARK_IMAGE_COUNT):
        stem = f"BCA001_{i:03d}_V1-0"
        _create_image(root / "raw" / "train" / "images" / f"{stem}.jpg", size=(1920, 1080))
        _create_label(root / "raw" / "train" / "labels" / f"{stem}.txt")
    return root


class TestDatasetBenchmark:
    def test_benchmark_scan(self, benchmark_dataset):
        scanner = DatasetScanner(benchmark_dataset)
        start = time.perf_counter()
        result = scanner.scan(splits=["train"])
        elapsed = time.perf_counter() - start
        assert result["summary"]["total_images"] == BENCHMARK_IMAGE_COUNT
        assert elapsed < 30.0

    def test_benchmark_validate(self, benchmark_dataset):
        validator = DatasetValidator(benchmark_dataset)
        start = time.perf_counter()
        result = validator.validate_all(splits=["train"])
        elapsed = time.perf_counter() - start
        assert result["summary"]["passed"] is True
        assert elapsed < 60.0

    def test_benchmark_statistics(self, benchmark_dataset):
        stats = DatasetStatistics(benchmark_dataset)
        start = time.perf_counter()
        result = stats.compute(splits=["train"])
        elapsed = time.perf_counter() - start
        assert result["images"]["total"] == BENCHMARK_IMAGE_COUNT
        assert elapsed < 60.0
