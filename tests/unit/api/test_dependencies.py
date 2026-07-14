import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from src.api.config import APIConfig
from src.api.dependencies import get_config, get_request_id


class TestDependencies:
    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.state.config = APIConfig()

        @app.get("/check-config")
        async def check_config(config=Depends(get_config)):
            return {"config_env": config.env.value}

        @app.get("/check-request-id")
        async def check_request_id(request_id=Depends(get_request_id)):
            return {"request_id": request_id}

        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_get_config(self, client):
        response = client.get("/check-config")
        assert response.status_code == 200
        data = response.json()
        assert data["config_env"] == "development"

    def test_get_request_id_default(self, client):
        response = client.get("/check-request-id")
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == "unknown"
