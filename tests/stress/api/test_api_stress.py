import pytest
from starlette.testclient import TestClient

from src.api.app import create_app
from src.api.config import APIConfig


class TestAPIStress:
    @classmethod
    def setup_class(cls):
        config = APIConfig()
        app = create_app(config)
        cls.client = TestClient(app)

    def test_concurrent_health_requests(self):
        for _ in range(50):
            r = self.client.get("/health")
            assert r.status_code == 200

    def test_mixed_endpoints(self):
        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/version"),
            ("GET", "/system"),
        ]
        for _ in range(20):
            for method, path in endpoints:
                r = self.client.request(method, path)
                assert r.status_code == 200

    def test_invalid_payloads(self):
        invalid_payloads = [
            {"image": 123},
            {},
            {"image": ""},
        ]
        for payload in invalid_payloads:
            r = self.client.post("/predict", json=payload)
            assert r.status_code in (422, 501)

    def test_rapid_even_odd_requests(self):
        for i in range(30):
            if i % 2 == 0:
                r = self.client.get("/")
            else:
                r = self.client.get("/health")
            assert r.status_code == 200
