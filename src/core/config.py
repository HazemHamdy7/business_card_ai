from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


class BaseConfig:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config: Dict[str, Any] = {}
        if config:
            self._config.update(config)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value

    def update(self, config: Dict[str, Any]) -> None:
        self._config.update(config)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._config)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "BaseConfig":
        return cls(config=config)

    @classmethod
    def from_json(cls, path: str) -> "BaseConfig":
        with open(path, "r") as f:
            data = json.load(f)
        return cls(config=data)

    @classmethod
    def from_yaml(cls, path: str) -> "BaseConfig":
        try:
            import yaml
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            return cls(config=data or {})
        except ImportError:
            raise ImportError("PyYAML is required to load YAML config files")
        except FileNotFoundError:
            return cls()

    @classmethod
    def from_env(cls, prefix: str = "BCA_") -> "BaseConfig":
        config: Dict[str, Any] = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        return cls(config=config)

    def merge_env(self, prefix: str = "BCA_") -> None:
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._config[config_key] = value
