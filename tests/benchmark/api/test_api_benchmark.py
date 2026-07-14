import time
import pytest
from starlette.testclient import TestClient

from src.api.app import create_app
from src.api.config import APIConfig


class TestAPIBenchmark:
    @classmethod
    def setup_class(cls):
        config = APIConfig()
        app = create_app(config)
        cls.client = TestClient(app)

    def test_root_throughput(self):
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            r = self.client.get("/")
            assert r.status_code == 200
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 10

    def test_health_throughput(self):
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            r = self.client.get("/health")
            assert r.status_code == 200
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 10
