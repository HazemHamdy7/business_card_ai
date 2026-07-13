from pathlib import Path
from typing import Any

import yaml

from src.core.exceptions import FileError


class YAMLIO:
    @staticmethod
    def load(path: Path, encoding: str = "utf-8") -> Any:
        try:
            with open(path, "r", encoding=encoding) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError as e:
            raise FileError(f"YAML file not found: {path}") from e
        except yaml.YAMLError as e:
            raise FileError(f"Invalid YAML in {path}: {e}") from e
        except Exception as e:
            raise FileError(f"Failed to load YAML from {path}: {e}") from e

    @staticmethod
    def save(data: Any, path: Path, encoding: str = "utf-8") -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding=encoding) as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise FileError(f"Failed to save YAML to {path}: {e}") from e
