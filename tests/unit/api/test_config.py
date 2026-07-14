import os
import pytest

from src.api.config import APIConfig, Environment


class TestEnvironment:
    def test_values(self):
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.TESTING.value == "testing"
        assert Environment.PRODUCTION.value == "production"


class TestAPIConfig:
    def test_default_config(self):
        config = APIConfig()
        assert config.env == Environment.DEVELOPMENT
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.log_level == "INFO"
        assert config.cors_origins == "*"
        assert config.reload is True
        assert config.is_development()

    def test_from_env(self):
        os.environ["APP_ENV"] = "testing"
        os.environ["API_HOST"] = "127.0.0.1"
        os.environ["API_PORT"] = "8080"
        try:
            config = APIConfig.from_env()
            assert config.env == Environment.TESTING
            assert config.host == "127.0.0.1"
            assert config.port == 8080
        finally:
            del os.environ["APP_ENV"]
            del os.environ["API_HOST"]
            del os.environ["API_PORT"]

    def test_from_env_production(self):
        os.environ["APP_ENV"] = "production"
        try:
            config = APIConfig.from_env()
            assert config.env == Environment.PRODUCTION
            assert config.is_production()
        finally:
            del os.environ["APP_ENV"]

    def test_is_production(self):
        dev = APIConfig()
        assert not dev.is_production()

        os.environ["APP_ENV"] = "production"
        try:
            prod = APIConfig()
            assert prod.is_production()
        finally:
            del os.environ["APP_ENV"]

    def test_secret_key_default(self):
        config = APIConfig()
        assert config.secret_key == "dev-secret-key"

    def test_debug_in_development(self):
        config = APIConfig()
        assert config.debug is True

    def test_debug_not_in_production(self):
        os.environ["APP_ENV"] = "production"
        try:
            config = APIConfig()
            assert config.debug is False
        finally:
            del os.environ["APP_ENV"]
