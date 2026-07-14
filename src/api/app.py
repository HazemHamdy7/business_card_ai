from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import APIConfig
from .exceptions import BusinessCardAIException
from .logging import get_logger, setup_logging
from .middleware import setup_middleware
from .response_models import ErrorResponse
from .routes import api_router
from .version import VERSION, TITLE, DESCRIPTION


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger = get_logger()
    config: APIConfig = app.state.config
    logger.info(
        f"API starting in {config.env.value} mode",
        extra={"version": VERSION},
    )
    yield
    logger.info("API shutting down")


def create_app(config: APIConfig | None = None) -> FastAPI:
    if config is None:
        config = APIConfig()
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version=VERSION,
        lifespan=lifespan,
        docs_url="/docs" if not config.is_production() else None,
        redoc_url="/redoc" if not config.is_production() else None,
        openapi_url="/openapi.json" if not config.is_production() else None,
    )

    app.state.config = config
    setup_logging(config.log_level)

    setup_middleware(app, config.cors_origins)
    app.include_router(api_router)
    _setup_exception_handlers(app)

    return app


def _setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorResponse(
                message="Validation error",
                status_code=422,
                details={"errors": errors},
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=str(exc.detail),
                status_code=exc.status_code,
            ).model_dump(),
        )

    @app.exception_handler(BusinessCardAIException)
    async def business_card_exception_handler(
        request: Request, exc: BusinessCardAIException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger = get_logger()
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="Internal server error",
                status_code=500,
            ).model_dump(),
        )
