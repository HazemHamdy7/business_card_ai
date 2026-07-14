import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    ExecutionTimeMiddleware,
    setup_middleware,
)


class TestMiddleware:
    @pytest.fixture
    def app(self):
        app = FastAPI()
        setup_middleware(app, cors_origins="*")

        @app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_request_id_added(self, client):
        response = client.get("/test")
        assert "X-Request-ID" in response.headers

    def test_execution_time_added(self, client):
        response = client.get("/test")
        assert "X-Execution-Time" in response.headers

    def test_cors_headers(self, client):
        response = client.options(
            "/test",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers

    def test_gzip_compression(self, client):
        response = client.get("/test", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200

    def test_custom_request_id(self, client):
        response = client.get("/test", headers={"X-Request-ID": "custom-id"})
        assert response.headers["X-Request-ID"] == "custom-id"
