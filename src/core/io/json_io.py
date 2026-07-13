import json
from pathlib import Path
from typing import Any

from src.core.exceptions import FileError


class JSONIO:
    @staticmethod
    def load(path: Path, encoding: str = "utf-8") -> Any:
        try:
            with open(path, "r", encoding=encoding) as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise FileError(f"JSON file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise FileError(f"Invalid JSON in {path}: {e}") from e
        except Exception as e:
            raise FileError(f"Failed to load JSON from {path}: {e}") from e

    @staticmethod
    def save(data: Any, path: Path, encoding: str = "utf-8", indent: int = 2) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise FileError(f"Failed to save JSON to {path}: {e}") from e
