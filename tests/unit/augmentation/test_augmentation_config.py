import os
import tempfile
import pytest

from src.augmentation.augmentation_config import AugmentationConfig, DEFAULT_CONFIG


class TestAugmentationConfig:
    def test_default_config(self):
        config = AugmentationConfig()
        assert config.rotation["enabled"]
        assert config.rotation["angle_range"] == [-15, 15]
        assert config.seed is None

    def test_from_dict_override(self):
        config = AugmentationConfig.from_dict({
            "rotation": {"enabled": False, "angle_range": [-30, 30]},
            "seed": 42,
        })
        assert config.seed == 42
        assert not config.rotation["enabled"]
        assert config.rotation["angle_range"] == [-30, 30]
        assert config.perspective["enabled"]

    def test_disable_all(self):
        config = AugmentationConfig()
        config.disable_all()
        assert not config.rotation["enabled"]
        assert not config.perspective["enabled"]
        assert not config.lighting["enabled"]
        assert not config.contrast["enabled"]
        assert not config.blur["enabled"]
        assert not config.noise["enabled"]
        assert not config.color["enabled"]

    def test_enable_all(self):
        config = AugmentationConfig()
        config.disable_all()
        config.enable_all()
        assert config.rotation["enabled"]
        assert config.color["enabled"]

    def test_is_enabled(self):
        config = AugmentationConfig()
        assert config.is_enabled("rotation")
        config.rotation["enabled"] = False
        assert not config.is_enabled("rotation")

    def test_is_enabled_unknown(self):
        config = AugmentationConfig()
        assert not config.is_enabled("unknown")

    def test_to_dict(self):
        config = AugmentationConfig(seed=42)
        d = config.to_dict()
        assert d["seed"] == 42
        assert "rotation" in d
        assert d["rotation"]["angle_range"] == [-15, 15]

    def test_from_yaml(self):
        yaml_content = """
seed: 123
rotation:
  enabled: false
  angle_range: [-45, 45]
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.close()
        try:
            config = AugmentationConfig.from_yaml(f.name)
            assert config.seed == 123
            assert not config.rotation["enabled"]
            assert config.rotation["angle_range"] == [-45, 45]
        finally:
            os.unlink(f.name)

    def test_from_yaml_missing_file(self):
        config = AugmentationConfig.from_yaml("nonexistent.yaml")
        assert isinstance(config, AugmentationConfig)
        assert config.rotation["enabled"]

    def test_config_immutable_defaults(self):
        c1 = AugmentationConfig()
        c2 = AugmentationConfig()
        c1.rotation["angle_range"] = [-90, 90]
        assert c2.rotation["angle_range"] == [-15, 15]
