from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthRequest(BaseModel):
    detailed: bool = Field(default=False, description="Include detailed health info")


class PredictionRequest(BaseModel):
    image: str = Field(..., description="Base64-encoded image data")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Prediction options")


class DatasetQuery(BaseModel):
    dataset_root: str = Field(default="dataset", description="Path to dataset root")
    train_label_dir: Optional[str] = Field(default=None)
    val_label_dir: Optional[str] = Field(default=None)
    test_label_dir: Optional[str] = Field(default=None)
    image_dir: Optional[str] = Field(default=None)
