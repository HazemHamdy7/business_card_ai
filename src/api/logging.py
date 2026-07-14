from __future__ import annotations

import logging
import sys
from typing import Dict, Optional


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        parts: Dict[str, str] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            parts["request_id"] = record.request_id
        if record.exc_info and record.exc_info[0]:
            parts["exception"] = self.formatException(record.exc_info)

        return " | ".join(f"{k}={v}" for k, v in parts.items())


def setup_logging(
    level: str = "INFO",
    name: str = "business_card_ai",
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "business_card_ai")
