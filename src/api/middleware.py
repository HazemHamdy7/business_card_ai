from __future__ import annotations

import time
import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .logging import get_logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(
            "X-Request-ID", str(uuid.uuid4())
        )
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        logger = get_logger()
        request_id = getattr(request.state, "request_id", "unknown")
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )
        response = await call_next(request)
        logger.info(
            f"Response: {response.status_code}",
            extra={"request_id": request_id},
        )
        return response


class ExecutionTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        response.headers["X-Execution-Time"] = f"{elapsed:.4f}s"
        return response


def setup_middleware(app: FastAPI, cors_origins: str = "*") -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins.split(",") if cors_origins != "*" else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(ExecutionTimeMiddleware)
    app.add_middleware(LoggingMiddleware)
