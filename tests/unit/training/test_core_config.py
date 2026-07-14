import os
import tempfile
import pytest

from src.core.config import BaseConfig


class TestBaseConfig:
    def test_defaults(self):
        c = BaseConfig()
        assert c.get("nonexistent") is None
        assert c.get("key", "default") == "default"

    def test_set_and_get(self):
        c = BaseConfig()
        c.set("key", "value")
        assert c.get("key") == "value"

    def test_update(self):
        c = BaseConfig()
        c.update({"a": 1, "b": 2})
        assert c.get("a") == 1
        assert c.get("b") == 2

    def test_to_dict(self):
        c = BaseConfig(config={"x": 10})
        d = c.to_dict()
        assert d["x"] == 10

    def test_from_dict(self):
        c = BaseConfig.from_dict({"y": 20})
        assert c.get("y") == 20

    def test_from_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"z": 30}')
            f.close()
        try:
            c = BaseConfig.from_json(f.name)
            assert c.get("z") == 30
        finally:
            os.unlink(f.name)

    def test_from_env(self):
        os.environ["BCA_TEST_KEY"] = "env_value"
        try:
            c = BaseConfig.from_env(prefix="BCA_")
            assert c.get("test_key") == "env_value"
        finally:
            del os.environ["BCA_TEST_KEY"]

    def test_merge_env(self):
        c = BaseConfig()
        os.environ["BCA_MERGE_KEY"] = "merged"
        try:
            c.merge_env("BCA_")
            assert c.get("merge_key") == "merged"
        finally:
            del os.environ["BCA_MERGE_KEY"]
