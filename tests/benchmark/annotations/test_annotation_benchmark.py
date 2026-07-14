import os
import tempfile
import time

import pytest

from src.annotations.annotation_validator import AnnotationValidator
from src.annotations.label_inspector import LabelInspector
from src.annotations.dataset_consistency_checker import DatasetConsistencyChecker
from src.annotations.annotation_statistics import AnnotationStatistics
from src.annotations.annotation_exporter import AnnotationExporter
from src.annotations.annotation_manager import AnnotationManager


NUM_LABELS = 50
NUM_LINES_PER_LABEL = 10


@pytest.fixture(scope="module")
def benchmark_label_dir():
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(NUM_LABELS):
            with open(os.path.join(tmp, f"img{i}.txt"), "w") as f:
                for j in range(NUM_LINES_PER_LABEL):
                    cls = j % 3
                    f.write(f"{cls} 0.5 0.5 0.2 0.3\n")
        yield tmp


@pytest.fixture(scope="module")
def benchmark_image_dir(benchmark_label_dir):
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(NUM_LABELS):
            with open(os.path.join(tmp, f"img{i}.jpg"), "w") as f:
                pass
        yield tmp


class TestAnnotationBenchmark:
    def test_benchmark_validator(self, benchmark_label_dir):
        validator = AnnotationValidator()
        start = time.perf_counter()
        for f in os.listdir(benchmark_label_dir):
            validator.validate_file(os.path.join(benchmark_label_dir, f))
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0

    def test_benchmark_inspector(self, benchmark_label_dir, benchmark_image_dir):
        inspector = LabelInspector()
        start = time.perf_counter()
        inspector.inspect(benchmark_label_dir, image_dir=benchmark_image_dir)
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0

    def test_benchmark_consistency(self, benchmark_label_dir, benchmark_image_dir):
        checker = DatasetConsistencyChecker()
        start = time.perf_counter()
        checker.check(benchmark_label_dir, benchmark_image_dir)
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0

    def test_benchmark_statistics(self, benchmark_label_dir):
        stats = AnnotationStatistics()
        start = time.perf_counter()
        stats.compute(benchmark_label_dir)
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0

    def test_benchmark_exporter(self, benchmark_label_dir):
        exporter = AnnotationExporter()
        validator = AnnotationValidator()
        results = [
            validator.validate_file(os.path.join(benchmark_label_dir, f))
            for f in os.listdir(benchmark_label_dir)
        ]
        with tempfile.TemporaryDirectory() as tmp:
            start = time.perf_counter()
            exporter.export_validation_to_json(results, os.path.join(tmp, "val.json"))
            elapsed = time.perf_counter() - start
            assert elapsed < 10.0

    def test_benchmark_manager(self, benchmark_label_dir, benchmark_image_dir):
        manager = AnnotationManager()
        with tempfile.TemporaryDirectory() as tmp:
            start = time.perf_counter()
            manager.run(benchmark_label_dir, image_dir=benchmark_image_dir, export_dir=tmp)
            elapsed = time.perf_counter() - start
            assert elapsed < 10.0
