import logging
import tempfile
from pathlib import Path

import pytest

from src.core.logger import get_logger, setup_logger


class TestLogger:
    def test_setup_logger_returns_logger(self) -> None:
        logger = setup_logger("test_logger", log_to_file=False, log_to_console=False)
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_default(self) -> None:
        logger = get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_logger_named(self) -> None:
        logger = get_logger("test")
        assert logger.name == "test"

    def test_logger_levels(self) -> None:
        logger = setup_logger("test_levels", log_to_file=False, log_to_console=False)
        logger.info("info test")
        logger.debug("debug test")
        logger.warning("warning test")
        logger.error("error test")

    def test_logger_success_level(self) -> None:
        logger = setup_logger("test_success", log_to_file=False, log_to_console=False)
        logger.success("success test")

    def test_setup_logger_creates_file(self, tmp_path: Path) -> None:
        from src.core.paths import Paths

        original_root = Paths._root
        Paths._root = tmp_path
        try:
            logger = setup_logger("test_file_logger", log_to_file=True, log_to_console=False)
            logger.info("test message")
            log_file = tmp_path / "logs" / "test_file_logger.log"
            assert log_file.exists()
            content = log_file.read_text(encoding="utf-8")
            assert "test message" in content
        finally:
            Paths._root = original_root
