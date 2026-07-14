import os
import tempfile
import pytest

from src.training.model_registry import ModelRegistry, ModelEntry


class TestModelRegistry:
    @pytest.fixture
    def registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield ModelRegistry(registry_dir=tmp)

    def test_register(self, registry):
        entry = registry.register("yolo_v8", "yolo", version="1.0.0")
        assert entry.model_id == "yolo_v8"
        assert entry.model_type == "yolo"
        assert entry.status == "registered"

    def test_get(self, registry):
        registry.register("yolo_v8", "yolo")
        entry = registry.get("yolo_v8")
        assert entry is not None
        assert entry.model_id == "yolo_v8"

    def test_list_models(self, registry):
        registry.register("yolo_v8", "yolo")
        registry.register("ocr_model", "ocr")
        all_models = registry.list_models()
        assert len(all_models) == 2
        yolo_models = registry.list_models(model_type="yolo")
        assert len(yolo_models) == 1

    def test_save_and_load_model(self, registry):
        registry.register("test_model", "test")
        state = {"weights": [1, 2, 3]}
        path = registry.save_model("test_model", state)
        assert os.path.isfile(path)
        loaded = registry.load_model("test_model")
        assert loaded is not None
        assert loaded["weights"] == [1, 2, 3]

    def test_update_metrics(self, registry):
        registry.register("test_model", "test")
        registry.update_metrics("test_model", {"mAP": 0.85, "precision": 0.9})
        entry = registry.get("test_model")
        assert entry.metrics["mAP"] == 0.85

    def test_register_future(self, registry):
        entry = registry.register_future("yolo", "Future YOLO model")
        assert entry.model_type == "yolo"
        assert entry.metadata.get("future_model") is True
        assert entry.version == "0.0.0"

    def test_entry_to_dict(self):
        entry = ModelEntry(
            model_id="test", model_type="yolo",
            version="1.0", metrics={"acc": 0.9},
        )
        d = entry.to_dict()
        assert d["model_id"] == "test"
        assert d["metrics"]["acc"] == 0.9

    def test_load_nonexistent_model(self, registry):
        result = registry.load_model("nonexistent")
        assert result is None

    def test_get_nonexistent(self, registry):
        entry = registry.get("nonexistent")
        assert entry is None
