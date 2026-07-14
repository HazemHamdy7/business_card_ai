import os
import tempfile
import time

import cv2
import numpy as np
import pytest

from src.dataset.dataset_quality import DatasetQuality
from src.dataset.duplicate_detector import DuplicateDetector


class TestDatasetBenchmark:
    @classmethod
    def setup_class(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.img_dir = cls.tmp.name
        for i in range(100):
            img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            path = os.path.join(cls.img_dir, f"img{i}.jpg")
            cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    @classmethod
    def teardown_class(cls):
        cls.tmp.cleanup()

    def test_quality_evaluation_speed(self):
        q = DatasetQuality()
        start = time.perf_counter()
        iterations = 10
        for _ in range(iterations):
            q.evaluate(self.img_dir)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 1

    def test_duplicate_detection_speed(self):
        d = DuplicateDetector()
        start = time.perf_counter()
        iterations = 5
        for _ in range(iterations):
            d.find_duplicates(self.img_dir)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 0.5
