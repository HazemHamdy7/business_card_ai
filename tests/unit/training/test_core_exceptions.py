from src.core.exceptions import (
    ConfigError, DeviceError, TrainingError, DatasetError,
)


class TestExceptions:
    def test_config_error(self):
        exc = ConfigError("bad config", {"field": "missing"})
        assert exc.message == "bad config"
        assert exc.status_code == 500
        assert exc.details["field"] == "missing"

    def test_device_error(self):
        exc = DeviceError("no gpu")
        assert exc.message == "no gpu"

    def test_training_error(self):
        exc = TrainingError("training failed")
        assert exc.message == "training failed"

    def test_dataset_error(self):
        exc = DatasetError("dataset not found")
        assert exc.message == "dataset not found"

    def test_inheritance(self):
        assert isinstance(ConfigError("x"), Exception)
        assert isinstance(DeviceError("x"), Exception)
