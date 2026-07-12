from pathlib import Path

import pytest
import yaml

from src.core.config import Config, EnvironmentLoader
from src.core.exceptions import ConfigurationError


class TestConfig:
    def test_config_singleton(self) -> None:
        c1 = Config()
        c2 = Config()
        assert c1 is c2

    def test_config_load_nonexistent(self) -> None:
        config = Config()
        data = config.load(Path("nonexistent.yaml"))
        assert data == {}

    def test_config_get_set(self) -> None:
        config = Config()
        config._data = {}
        config.set("model.type", "yolo")
        assert config.get("model.type") == "yolo"

    def test_config_get_default(self) -> None:
        config = Config()
        config._data = {}
        assert config.get("nonexistent", "default") == "default"

    def test_config_get_nonexistent(self) -> None:
        config = Config()
        config._data = {}
        assert config.get("nonexistent") is None

    def test_config_save_and_load(self, tmp_path: Path) -> None:
        config = Config()
        config._data = {}
        config.set("test.key", "value")
        config_path = tmp_path / "test_config.yaml"
        config.save(config_path)
        assert config_path.exists()

        config2 = Config()
        data = config2.load(config_path)
        assert data == {"test": {"key": "value"}}

    def test_config_data_property(self) -> None:
        config = Config()
        config._data = {"a": 1}
        assert config.data == {"a": 1}
