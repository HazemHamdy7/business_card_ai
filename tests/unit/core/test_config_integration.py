from pathlib import Path

import yaml

from src.core.config import Config


class TestConfigIntegration:
    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.yaml"
        config = Config()
        config._data = {}
        config.set("model.name", "test_model")
        config.set("model.params.learning_rate", 0.001)
        config.save(config_path)

        loaded = Config()
        data = loaded.load(config_path)
        assert data["model"]["name"] == "test_model"
        assert data["model"]["params"]["learning_rate"] == 0.001

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: [yaml\n", encoding="utf-8")
        config = Config()
        import pytest
        from src.core.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError):
            config.load(config_path)
