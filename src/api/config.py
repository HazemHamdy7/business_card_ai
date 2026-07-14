from __future__ import annotations

import os
from enum import Enum
from typing import Optional


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class APIConfig:
    def __init__(self) -> None:
        self.env: Environment = Environment(
            os.getenv("APP_ENV", "development")
        )
        self.host: str = os.getenv("API_HOST", "0.0.0.0")
        self.port: int = int(os.getenv("API_PORT", "8000"))
        self.reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
        self.log_level: str = os.getenv("API_LOG_LEVEL", "INFO")
        self.cors_origins: str = os.getenv(
            "API_CORS_ORIGINS", "*"
        )
        self.request_id_header: str = os.getenv(
            "API_REQUEST_ID_HEADER", "X-Request-ID"
        )
        self.gzip_min_size: int = int(
            os.getenv("API_GZIP_MIN_SIZE", "1000")
        )
        self.db_url: Optional[str] = os.getenv("DATABASE_URL")
        self.redis_url: Optional[str] = os.getenv("REDIS_URL")
        self.secret_key: str = os.getenv("API_SECRET_KEY", "dev-secret-key")
        self.debug: bool = self.env == Environment.DEVELOPMENT

    @classmethod
    def from_env(cls) -> "APIConfig":
        return cls()

    def is_development(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    def is_testing(self) -> bool:
        return self.env == Environment.TESTING

    def is_production(self) -> bool:
        return self.env == Environment.PRODUCTION
