from __future__ import annotations

from .app import create_app
from .config import APIConfig
from .logging import get_logger


def run_server(config: APIConfig) -> None:
    import uvicorn

    logger = get_logger()
    logger.info(
        f"Starting server on {config.host}:{config.port}",
        extra={"env": config.env.value},
    )

    uvicorn.run(
        "src.api.app:create_app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower(),
        factory=True,
    )
