from __future__ import annotations

__version__ = "0.1.0"
__title__ = "Business Card AI API"
__description__ = "Production-ready REST API for Business Card AI"

from .app import create_app
from .server import run_server
from .config import APIConfig, Environment
from .exceptions import BusinessCardAIException, ResourceNotFoundException
from .response_models import (
    ErrorResponse,
    HealthResponse,
    PredictionResponse,
    DatasetInfoResponse,
    AnnotationResponse,
    SystemInfoResponse,
    APIInfoResponse,
)

__all__ = [
    "create_app",
    "run_server",
    "APIConfig",
    "Environment",
    "BusinessCardAIException",
    "ResourceNotFoundException",
    "ErrorResponse",
    "HealthResponse",
    "PredictionResponse",
    "DatasetInfoResponse",
    "AnnotationResponse",
    "SystemInfoResponse",
    "APIInfoResponse",
]
