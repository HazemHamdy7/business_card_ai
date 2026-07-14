from __future__ import annotations

from fastapi import APIRouter

from .health_routes import router as health_router
from .dataset_routes import router as dataset_router
from .annotation_routes import router as annotation_router
from .prediction_routes import router as prediction_router
from .system_routes import router as system_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(dataset_router)
api_router.include_router(annotation_router)
api_router.include_router(prediction_router)
api_router.include_router(system_router)

__all__ = ["api_router"]
