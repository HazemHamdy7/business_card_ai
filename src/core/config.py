import os
from pathlib import Path
from typing import Any

import yaml

from src.core.exceptions import ConfigurationError
from src.core.paths import Paths


class Config:
    _instance: "Config | None" = None
    _data: dict[str, Any] = {}

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: Path | None = None) -> dict[str, Any]:
        path = config_path or Paths.config_file()
        if not path.exists():
            self._data = {}
            return self._data

        try:
            with open(path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {path}: {e}") from e

        return self._data

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value: Any = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        target = self._data
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def save(self, config_path: Path | None = None) -> None:
        path = config_path or Paths.config_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(self._data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to save config to {path}: {e}") from e

    @property
    def data(self) -> dict[str, Any]:
        return self._data


class EnvironmentLoader:
    def __init__(self, env_file: Path | None = None) -> None:
        self._env_file = env_file or Paths.env_file()
        self._variables: dict[str, str] = {}

    def load(self) -> dict[str, str]:
        if not self._env_file.exists():
            self._variables = {}
            return self._variables

        with open(self._env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("\"'")
                self._variables[key] = value
                os.environ.setdefault(key, value)

        return self._variables

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._variables.get(key, os.environ.get(key, default))

    @property
    def variables(self) -> dict[str, str]:
        return dict(self._variables)
