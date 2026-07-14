import io
import logging
import sys

import pytest

from src.api.logging import StructuredFormatter, setup_logging, get_logger


class TestStructuredFormatter:
    def test_format_basic(self):
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="hello", args=None, exc_info=None,
        )
        formatted = formatter.format(record)
        assert "level=INFO" in formatted
        assert "name=test" in formatted
        assert "message=hello" in formatted
        assert "timestamp=" in formatted

    def test_format_with_request_id(self):
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="req", args=None, exc_info=None,
        )
        record.request_id = "abc-123"
        formatted = formatter.format(record)
        assert "request_id=abc-123" in formatted


class TestSetupLogging:
    def test_setup_logging(self):
        logger = setup_logging(level="DEBUG", name="test_logger")
        assert logger.level == logging.DEBUG
        assert logger.name == "test_logger"
        assert len(logger.handlers) == 1

    def test_get_logger(self):
        logger = get_logger("test_logger_get")
        assert logger.name == "test_logger_get"

    def test_get_logger_default(self):
        logger = get_logger()
        assert logger.name == "business_card_ai"
