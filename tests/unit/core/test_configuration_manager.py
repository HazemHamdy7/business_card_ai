import os
from pathlib import Path

import pytest

from src.core.config import (
    ConfigurationManager,
    ConfigurationSource,
    ConfigurationValidator,
    EnvironmentConfigurationSource,
    JsonConfigurationSource,
    YamlConfigurationSource,
)
from src.core.exceptions import ConfigurationError, ValidationError


class TestYamlConfigurationSource:
    def test_load_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "test.yaml"
        path.write_text("key: value\nnested:\n  inner: 42\n", encoding="utf-8")
        source = YamlConfigurationSource(path)
        data = source.load()
        assert data["key"] == "value"
        assert data["nested"]["inner"] == 42

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        source = YamlConfigurationSource(tmp_path / "nonexistent.yaml")
        assert source.load() == {}

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "invalid.yaml"
        path.write_text("invalid: [yaml\n", encoding="utf-8")
        source = YamlConfigurationSource(path)
        with pytest.raises(ConfigurationError):
            source.load()

    def test_name(self, tmp_path: Path) -> None:
        source = YamlConfigurationSource(tmp_path / "test.yaml")
        assert "test.yaml" in source.name()


class TestJsonConfigurationSource:
    def test_load_json(self, tmp_path: Path) -> None:
        path = tmp_path / "test.json"
        path.write_text('{"key": "value", "nested": {"inner": 42}}', encoding="utf-8")
        source = JsonConfigurationSource(path)
        data = source.load()
        assert data["key"] == "value"
        assert data["nested"]["inner"] == 42

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        source = JsonConfigurationSource(tmp_path / "nonexistent.json")
        assert source.load() == {}

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "invalid.json"
        path.write_text("{invalid}", encoding="utf-8")
        source = JsonConfigurationSource(path)
        with pytest.raises(ConfigurationError):
            source.load()

    def test_name(self, tmp_path: Path) -> None:
        source = JsonConfigurationSource(tmp_path / "test.json")
        assert "test.json" in source.name()


class TestEnvironmentConfigurationSource:
    def test_empty(self) -> None:
        source = EnvironmentConfigurationSource("NONEXISTENT_PREFIX_XYZ_")
        data = source.load()
        assert data == {}

    def test_with_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BCA_MODEL_TYPE", "yolo")
        monkeypatch.setenv("BCA_TRAINING_EPOCHS", "100")
        monkeypatch.setenv("BCA_DEBUG", "true")
        source = EnvironmentConfigurationSource("BCA_")
        data = source.load()
        assert data["model"]["type"] == "yolo"
        assert data["training"]["epochs"] == 100
        assert data["debug"] is True


class TestConfigurationValidator:
    def test_validate_type_string(self) -> None:
        ConfigurationValidator.validate_type("hello", str, "key")

    def test_validate_type_error(self) -> None:
        with pytest.raises(ValidationError):
            ConfigurationValidator.validate_type(42, str, "key")

    def test_validate_data(self) -> None:
        ConfigurationValidator.validate({"a": 1})

    def test_validate_not_dict(self) -> None:
        with pytest.raises(ValidationError):
            ConfigurationValidator.validate("not dict")

    def test_validate_with_schema(self) -> None:
        data = {"model": {"type": "yolo", "epochs": 100}}
        schema = {"model.type": str, "model.epochs": int}
        ConfigurationValidator.validate(data, schema)

    def test_validate_with_schema_error(self) -> None:
        data = {"model": {"type": 42}}
        schema = {"model.type": str}
        with pytest.raises(ValidationError):
            ConfigurationValidator.validate(data, schema)


class TestConfigurationManager:
    def test_load_creates_config_files(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        for name in ["development.yaml", "production.yaml", "training.yaml", "inference.yaml"]:
            assert (tmp_path / name).exists()

    def test_get_default(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        assert cm.get("nonexistent") is None
        assert cm.get("nonexistent", "default") == "default"

    def test_set_and_get(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        cm.set("model.type", "yolo")
        assert cm.get("model.type") == "yolo"

    def test_typed_getters(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        cm.set("str_val", "hello")
        cm.set("int_val", 42)
        cm.set("float_val", 3.14)
        cm.set("bool_val", True)
        cm.set("list_val", [1, 2, 3])
        cm.set("dict_val", {"a": 1})

        assert cm.get_string("str_val") == "hello"
        assert cm.get_int("int_val") == 42
        assert cm.get_float("float_val") == 3.14
        assert cm.get_bool("bool_val") is True
        assert cm.get_list("list_val") == [1, 2, 3]
        assert cm.get_dict("dict_val") == {"a": 1}

    def test_typed_getters_validation(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        cm.set("val", 42)
        with pytest.raises(ValidationError):
            cm.get_string("val")

    def test_typed_getters_with_defaults(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        assert cm.get_string("missing", "default") == "default"
        assert cm.get_int("missing", 10) == 10
        assert cm.get_bool("missing", True) is True
        assert cm.get_float("missing", 1.5) == 1.5

    def test_set_defaults(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.set_defaults({"app": {"mode": "default"}})
        cm.load()
        assert cm.get("app.mode") == "default"

    def test_environment_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        dev_path = tmp_path / "development.yaml"
        dev_path.write_text("model:\n  type: file_yolo\n", encoding="utf-8")
        monkeypatch.setenv("BCA_MODEL_TYPE", "env_yolo")
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        assert cm.get("model.type") == "env_yolo"

    def test_data_property(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        cm.set("a", 1)
        assert isinstance(cm.data, dict)
        assert cm.data["a"] == 1

    def test_add_custom_source(self, tmp_path: Path) -> None:
        class TestSource(ConfigurationSource):
            def load(self) -> dict:
                return {"custom": "value"}
            def name(self) -> str:
                return "test"
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.add_source(TestSource())
        cm.load()
        assert cm.get("custom") == "value"

    def test_reload(self, tmp_path: Path) -> None:
        cm = ConfigurationManager(config_dir=tmp_path)
        cm.load()
        cm.set("k", "v1")
        data = cm.reload()
        assert isinstance(data, dict)
