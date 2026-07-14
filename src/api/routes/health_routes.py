from __future__ import annotations

from fastapi import APIRouter, Depends

from ..config import APIConfig
from ..dependencies import get_config
from ..health import get_health_info, get_system_info
from ..response_models import APIInfoResponse, HealthResponse, SystemInfoResponse
from ..version import get_version_info

router = APIRouter(tags=["Health"])


@router.get("/", response_model=APIInfoResponse)
async def root() -> APIInfoResponse:
    info = get_version_info()
    return APIInfoResponse(
        title=info["title"],
        version=info["version"],
        api_version=info["api_version"],
        description=info["description"],
        status="running",
    )


@router.get("/health", response_model=HealthResponse)
async def health(
    config: APIConfig = Depends(get_config),
) -> HealthResponse:
    info = get_health_info(config)
    return HealthResponse(
        status=info["status"],
        version=info["version"],
        python_version=info["python_version"],
        gpu_available=info["gpu_available"],
        cuda_available=info["cuda_available"],
        memory_usage=info["memory_usage"],
        disk_usage=info["disk_usage"],
        uptime=f"{info['uptime_seconds']}s",
    )


@router.get("/version")
async def version() -> dict:
    return get_version_info()
