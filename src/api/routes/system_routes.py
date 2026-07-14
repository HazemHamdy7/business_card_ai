from __future__ import annotations

from fastapi import APIRouter

from ..health import get_system_info
from ..response_models import SystemInfoResponse

router = APIRouter(tags=["System"])


@router.get("/system", response_model=SystemInfoResponse)
async def system_info() -> SystemInfoResponse:
    info = get_system_info()
    return SystemInfoResponse(
        python_version=info["python_version"],
        platform=info["platform"],
        cpu_count=info["cpu_count"],
        memory=info["memory"],
        environment=info["environment"],
    )
