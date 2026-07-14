from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "An error occurred"
    status_code: int = 500
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
    python_version: str = ""
    gpu_available: bool = False
    cuda_available: bool = False
    memory_usage: Optional[Dict[str, Any]] = None
    disk_usage: Optional[Dict[str, Any]] = None
    uptime: Optional[str] = None


class PredictionResponse(BaseModel):
    success: bool = True
    message: str = "Prediction pipeline is not implemented yet."
    predictions: Optional[List[Dict[str, Any]]] = None


class DatasetInfoResponse(BaseModel):
    ready: bool = False
    quality_score: float = 0.0
    total_images: int = 0
    total_labels: int = 0
    num_classes: int = 0
    total_objects: int = 0
    imbalance_score: float = 0.0


class AnnotationResponse(BaseModel):
    ready: bool = False
    total_files: int = 0
    total_objects: int = 0
    valid_files: int = 0
    invalid_files: int = 0


class SystemInfoResponse(BaseModel):
    python_version: str = ""
    platform: str = ""
    cpu_count: int = 0
    memory: Optional[Dict[str, Any]] = None
    environment: str = "development"


class APIInfoResponse(BaseModel):
    title: str = "Business Card AI API"
    version: str = "0.1.0"
    api_version: str = "v1"
    description: str = ""
    status: str = "running"
