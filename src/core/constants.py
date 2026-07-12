from typing import Final

PROJECT_NAME: Final[str] = "Business Card AI"
PROJECT_VERSION: Final[str] = "0.1.0"
PROJECT_DESCRIPTION: Final[str] = "Offline AI-powered Business Card Recognition and Classification"

DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_CONFIG_DIR: Final[str] = "config"
DEFAULT_DATASET_DIR: Final[str] = "dataset"
DEFAULT_MODELS_DIR: Final[str] = "models"
DEFAULT_LOGS_DIR: Final[str] = "logs"
DEFAULT_DOCS_DIR: Final[str] = "docs"
DEFAULT_CONFIG_FILE: Final[str] = "config.yaml"
DEFAULT_ENV_FILE: Final[str] = ".env"

LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES: Final[int] = 10 * 1024 * 1024
LOG_BACKUP_COUNT: Final[int] = 5

SUCCESS_LEVEL: Final[int] = 25

TIMER_PRECISION: Final[int] = 6
