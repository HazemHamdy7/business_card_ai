from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Request

from .config import APIConfig


async def get_config(request: Request) -> APIConfig:
    return request.app.state.config


async def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


async def get_api_config() -> AsyncGenerator[APIConfig, None]:
    yield APIConfig.from_env()
