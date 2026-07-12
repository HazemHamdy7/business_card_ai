from src.core.constants import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_CONFIG_FILE,
    DEFAULT_DATASET_DIR,
    DEFAULT_DOCS_DIR,
    DEFAULT_ENCODING,
    DEFAULT_ENV_FILE,
    DEFAULT_LOGS_DIR,
    DEFAULT_MODELS_DIR,
    LOG_BACKUP_COUNT,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    LOG_MAX_BYTES,
    PROJECT_DESCRIPTION,
    PROJECT_NAME,
    PROJECT_VERSION,
    SUCCESS_LEVEL,
    TIMER_PRECISION,
)


class TestConstants:
    def test_project_name(self) -> None:
        assert PROJECT_NAME == "Business Card AI"

    def test_project_version(self) -> None:
        assert PROJECT_VERSION == "0.1.0"

    def test_project_description(self) -> None:
        assert "Business Card" in PROJECT_DESCRIPTION

    def test_default_encoding(self) -> None:
        assert DEFAULT_ENCODING == "utf-8"

    def test_default_dirs(self) -> None:
        assert DEFAULT_CONFIG_DIR == "config"
        assert DEFAULT_DATASET_DIR == "dataset"
        assert DEFAULT_MODELS_DIR == "models"
        assert DEFAULT_LOGS_DIR == "logs"
        assert DEFAULT_DOCS_DIR == "docs"

    def test_log_constants(self) -> None:
        assert LOG_FORMAT is not None
        assert LOG_DATE_FORMAT is not None
        assert LOG_MAX_BYTES > 0
        assert LOG_BACKUP_COUNT > 0

    def test_success_level(self) -> None:
        assert SUCCESS_LEVEL == 25

    def test_timer_precision(self) -> None:
        assert TIMER_PRECISION == 6
