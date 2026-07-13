import logging
from logging.handlers import RotatingFileHandler
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

from src.core.constants import LOG_BACKUP_COUNT, LOG_DATE_FORMAT, LOG_FORMAT, LOG_MAX_BYTES, SUCCESS_LEVEL
from src.core.paths import Paths

logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

_console = Console()


def success(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


logging.Logger.success = success  # type: ignore[attr-defined]


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: "dim blue",
        logging.INFO: "green",
        SUCCESS_LEVEL: "bold green",
        logging.WARNING: "yellow",
        logging.ERROR: "bold red",
        logging.CRITICAL: "bold red on white",
    }

    def format(self, record: logging.LogRecord) -> str:
        level_name = record.levelname
        color = self.LEVEL_COLORS.get(record.levelno, "")
        if color:
            record.levelname = f"[{color}]{level_name}[/{color.split()[0]}]"
        return super().format(record)


def setup_logger(
    name: str = "business_card_ai",
    level: int = logging.DEBUG,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    if log_to_console:
        rich_handler = RichHandler(
            console=Console(),
            show_time=True,
            show_path=False,
            show_level=True,
            rich_tracebacks=True,
        )
        rich_handler.setLevel(level)
        logger.addHandler(rich_handler)

    if log_to_file:
        log_dir = Paths.logs_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=log_dir / f"{name}.log",
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name or "business_card_ai")
