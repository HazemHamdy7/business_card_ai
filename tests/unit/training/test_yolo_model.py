from __future__ import annotations

import os
import tempfile

import pytest

from src.training.yolo_config import YOLOModelConfig
from src.training.yolo_model import YOLOModel, YOLOModelInfo, ARCH_SCALE


class TestYOLOModel:
    def test_build_default(self):
        config = YOLOModelConfig()
        model = YOLOModel(config)
        info = model.build()
        assert isinstance(info, YOLOModelInfo)
        assert info.arch == "n"
        assert info.input_size == 640
        assert info.num_classes == 1
        assert info.model_id == "yolon_business_card"
        assert not info.pretrained
        assert model.model is None

    def test_build_all_archs(self):
        for arch in ["n", "s", "m", "l", "x"]:
            config = YOLOModelConfig(arch=arch)
            model = YOLOModel(config)
            info = model.build()
            assert info.arch == arch
            assert arch in info.model_id
            assert info.layers > 0
            assert "scale_factors" in info.metadata

    def test_build_with_pretrained(self):
        config = YOLOModelConfig(arch="m", pretrained=True, num_classes=2)
        model = YOLOModel(config)
        info = model.build()
        assert info.pretrained
        assert info.num_classes == 2

    def test_load_weights(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            weight_path = os.path.join(tmpdir, "yolo.pt")
            with open(weight_path, "w") as f:
                f.write("dummy")
            config = YOLOModelConfig()
            model = YOLOModel(config)
            model.build()
            model.load_weights(weight_path)
            assert model.info
            assert model.info.weight_path == weight_path
            assert model.info.pretrained

    def test_load_weights_file_not_found(self):
        config = YOLOModelConfig()
        model = YOLOModel(config)
        model.build()
        with pytest.raises(FileNotFoundError):
            model.load_weights("nonexistent.pt")

    def test_get_expected_input_shape(self):
        config = YOLOModelConfig(input_size=640)
        model = YOLOModel(config)
        shape = model.get_expected_input_shape()
        assert shape == (1, 3, 640, 640)

    def test_get_expected_input_shape_varied(self):
        config = YOLOModelConfig(input_size=416)
        model = YOLOModel(config)
        assert model.get_expected_input_shape() == (1, 3, 416, 416)

    def test_summary_before_build(self):
        config = YOLOModelConfig()
        model = YOLOModel(config)
        assert model.summary() == {"status": "not_built"}

    def test_summary_after_build(self):
        config = YOLOModelConfig(arch="x", input_size=1280)
        model = YOLOModel(config)
        model.build()
        summary = model.summary()
        assert summary["arch"] == "x"
        assert summary["input_size"] == 1280

    def test_info_property(self):
        config = YOLOModelConfig()
        model = YOLOModel(config)
        assert model.info is None
        model.build()
        assert model.info is not None

    def test_get_freeze_layers_default(self):
        config = YOLOModelConfig()
        model = YOLOModel(config)
        assert model.get_freeze_layers() == []

    def test_get_freeze_layers_backbone(self):
        config = YOLOModelConfig(freeze={"backbone": True})
        model = YOLOModel(config)
        frozen = model.get_freeze_layers()
        assert "backbone" in frozen

    def test_get_freeze_layers_all(self):
        config = YOLOModelConfig(freeze={"backbone": True, "neck": True, "head": True})
        model = YOLOModel(config)
        frozen = model.get_freeze_layers()
        assert "backbone" in frozen
        assert "neck" in frozen
        assert "head" in frozen

    def test_get_freeze_layers_custom(self):
        config = YOLOModelConfig(freeze={"layers": [3, 7, 11]})
        model = YOLOModel(config)
        frozen = model.get_freeze_layers()
        assert "3" in frozen
        assert "7" in frozen
        assert "11" in frozen

    def test_arch_scale_values(self):
        assert ARCH_SCALE["n"]["depth"] == 0.33
        assert ARCH_SCALE["n"]["width"] == 0.25
        assert ARCH_SCALE["s"]["width"] == 0.50
        assert ARCH_SCALE["m"]["width"] == 0.75
        assert ARCH_SCALE["l"]["depth"] == 1.0
        assert ARCH_SCALE["l"]["width"] == 1.0
        assert ARCH_SCALE["x"]["width"] == 1.25

    def test_build_layers_scaling(self):
        config = YOLOModelConfig(arch="x")
        model = YOLOModel(config)
        info = model.build()
        assert info.layers >= 3
        assert "base_channels" in info.metadata
