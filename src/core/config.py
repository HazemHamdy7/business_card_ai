import json
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from src.core.constants import CONFIG_DEVELOPMENT, CONFIG_INFERENCE, CONFIG_PRODUCTION, CONFIG_TRAINING
from src.core.exceptions import ConfigurationError, FileError, ValidationError
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


class ConfigurationSource(ABC):
    @abstractmethod
    def load(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class YamlConfigurationSource(ConfigurationSource):
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {self._path}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load YAML from {self._path}: {e}") from e

    def name(self) -> str:
        return str(self._path)


class JsonConfigurationSource(ConfigurationSource):
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {self._path}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load JSON from {self._path}: {e}") from e

    def name(self) -> str:
        return str(self._path)


class EnvironmentConfigurationSource(ConfigurationSource):
    def __init__(self, prefix: str = "BCA_"):
        self._prefix = prefix

    def load(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, val in sorted(os.environ.items()):
            if key.startswith(self._prefix):
                stripped = key[len(self._prefix):].lower()
                keys = stripped.split("_")
                self._deep_set(result, keys, self._parse_value(val))
        return result

    def name(self) -> str:
        return f"env:{self._prefix}"

    @staticmethod
    def _deep_set(d: dict[str, Any], keys: list[str], value: Any) -> None:
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    @staticmethod
    def _parse_value(val: str) -> Any:
        val = val.strip()
        if val.lower() in ("true", "1"):
            return True
        if val.lower() in ("false", "0"):
            return False
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return val


class ConfigurationValidator:
    @staticmethod
    def validate_type(value: Any, expected_type: type, key: str) -> None:
        if not isinstance(value, expected_type):
            raise ValidationError(f"Key '{key}' expected {expected_type.__name__}, got {type(value).__name__}")

    @staticmethod
    def validate(data: dict[str, Any], schema: dict[str, Any] | None = None) -> None:
        if not isinstance(data, dict):
            raise ValidationError(f"Data must be a dict, got {type(data).__name__}")
        if schema is None:
            return
        for key, expected_type in schema.items():
            keys = key.split(".")
            value = data
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = None
                    break
            if value is not None:
                if not isinstance(value, expected_type):
                    raise ValidationError(f"Key '{key}' expected {expected_type.__name__}, got {type(value).__name__}")


class ConfigurationManager:
    def __init__(self, config_dir: Path | None = None, prefix: str = "BCA_"):
        self._config_dir = config_dir or Paths.config_dir()
        self._prefix = prefix
        self._data: dict[str, Any] = {}
        self._defaults: dict[str, Any] = {}
        self._last_loaded = 0.0
        self._reload_interval: float | None = None
        self._sources: list[ConfigurationSource] = []
        self._validator = ConfigurationValidator()
        self._register_defaults()

    def _register_defaults(self) -> None:
        dev_path = self._config_dir / CONFIG_DEVELOPMENT
        prod_path = self._config_dir / CONFIG_PRODUCTION
        train_path = self._config_dir / CONFIG_TRAINING
        infer_path = self._config_dir / CONFIG_INFERENCE

        for p in [dev_path, prod_path, train_path, infer_path]:
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text("{}\n", encoding="utf-8")

    def add_source(self, source: ConfigurationSource) -> None:
        self._sources.append(source)

    def load(self) -> dict[str, Any]:
        sources: list[ConfigurationSource] = []

        for path_name in [CONFIG_DEVELOPMENT, CONFIG_PRODUCTION, CONFIG_TRAINING, CONFIG_INFERENCE]:
            path = self._config_dir / path_name
            if path.suffix == ".yaml":
                sources.append(YamlConfigurationSource(path))
            elif path.suffix == ".json":
                sources.append(JsonConfigurationSource(path))

        sources += self._sources
        sources.append(EnvironmentConfigurationSource(self._prefix))

        merged: dict[str, Any] = {}
        for source in sources:
            try:
                data = source.load()
                self._deep_merge(merged, data)
            except ConfigurationError:
                continue

        self._deep_merge(merged, self._defaults)
        self._data = merged
        self._last_loaded = time.time()
        return self._data

    def reload(self) -> dict[str, Any]:
        return self.load()

    def enable_auto_reload(self, interval: float = 5.0) -> None:
        self._reload_interval = interval

    def disable_auto_reload(self) -> None:
        self._reload_interval = None

    def get(self, key: str, default: Any = None) -> Any:
        self._auto_reload_if_needed()
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

    def get_string(self, key: str, default: str | None = None) -> str | None:
        value = self.get(key, default)
        if value is not None and not isinstance(value, str):
            raise ValidationError(f"Key '{key}' expected string, got {type(value).__name__}")
        return value

    def get_int(self, key: str, default: int | None = None) -> int | None:
        value = self.get(key, default)
        if value is not None and not isinstance(value, int):
            raise ValidationError(f"Key '{key}' expected int, got {type(value).__name__}")
        return value

    def get_bool(self, key: str, default: bool | None = None) -> bool | None:
        value = self.get(key, default)
        if value is not None and not isinstance(value, bool):
            raise ValidationError(f"Key '{key}' expected bool, got {type(value).__name__}")
        return value

    def get_float(self, key: str, default: float | None = None) -> float | None:
        value = self.get(key, default)
        if value is not None and not isinstance(value, (float, int)):
            raise ValidationError(f"Key '{key}' expected float, got {type(value).__name__}")
        return float(value) if isinstance(value, int) else value

    def get_list(self, key: str, default: list | None = None) -> list | None:
        value = self.get(key, default)
        if value is not None and not isinstance(value, list):
            raise ValidationError(f"Key '{key}' expected list, got {type(value).__name__}")
        return value

    def get_dict(self, key: str, default: dict | None = None) -> dict | None:
        value = self.get(key, default)
        if value is not None and not isinstance(value, dict):
            raise ValidationError(f"Key '{key}' expected dict, got {type(value).__name__}")
        return value

    @property
    def data(self) -> dict[str, Any]:
        self._auto_reload_if_needed()
        return self._data

    @property
    def defaults(self) -> dict[str, Any]:
        return self._defaults

    def set_defaults(self, data: dict[str, Any]) -> None:
        self._defaults = data

    def _auto_reload_if_needed(self) -> None:
        if self._reload_interval is not None:
            if time.time() - self._last_loaded > self._reload_interval:
                self.load()

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                ConfigurationManager._deep_merge(base[key], val)
            else:
                base[key] = val
