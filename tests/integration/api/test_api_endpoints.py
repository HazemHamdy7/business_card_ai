import pytest
from starlette.testclient import TestClient

from src.api.app import create_app
from src.api.config import APIConfig


class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        config = APIConfig()
        app = create_app(config)
        return TestClient(app)

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["title"] == "Business Card AI API"
        assert data["version"] == "0.1.0"

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert "python_version" in data

    def test_version_endpoint(self, client):
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "0.1.0"

    def test_system_endpoint(self, client):
        response = client.get("/system")
        assert response.status_code == 200
        data = response.json()
        assert "python_version" in data
        assert data["cpu_count"] >= 1

    def test_dataset_status_endpoint(self, client):
        response = client.get("/dataset/status")
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data

    def test_annotation_status_endpoint(self, client):
        response = client.get("/annotation/status")
        assert response.status_code == 200

    def test_predict_not_implemented(self, client):
        response = client.post("/predict", json={"image": "test"})
        assert response.status_code == 501

    def test_detect_not_implemented(self, client):
        response = client.post("/detect")
        assert response.status_code == 501

    def test_ocr_not_implemented(self, client):
        response = client.post("/ocr")
        assert response.status_code == 501

    def test_business_card_not_implemented(self, client):
        response = client.post("/business-card")
        assert response.status_code == 501

    def test_404_on_unknown_route(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_request_id_header(self, client):
        response = client.get("/health")
        assert "X-Request-ID" in response.headers

    def test_execution_time_header(self, client):
        response = client.get("/health")
        assert "X-Execution-Time" in response.headers

    def test_cors_headers(self, client):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers
