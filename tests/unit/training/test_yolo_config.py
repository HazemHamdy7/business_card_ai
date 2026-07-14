from __future__ import annotations

import pytest

from src.training.yolo_config import (
    YOLOModelConfig,
    YOLONMSConfig,
    YOLOAugmentationConfig,
    YOLOFreezeConfig,
    YOLO_ARCH_TYPES,
    YOLO_INPUT_SIZES,
)


class TestYOLOModelConfig:
    def test_default_config(self):
        config = YOLOModelConfig()
        assert config.arch == "n"
        assert config.input_size == 640
        assert config.num_classes == 1
        assert config.class_names == {0: "business_card"}
        assert not config.pretrained

    def test_valid_arch(self):
        for arch in YOLO_ARCH_TYPES:
            config = YOLOModelConfig(arch=arch)
            assert config.arch == arch

    def test_invalid_arch(self):
        with pytest.raises(ValueError, match="Invalid YOLO architecture"):
            YOLOModelConfig(arch="z")

    def test_invalid_input_size(self):
        with pytest.raises(ValueError, match="Invalid input size"):
            YOLOModelConfig(input_size=256)

    def test_valid_input_sizes(self):
        for size in YOLO_INPUT_SIZES:
            config = YOLOModelConfig(input_size=size)
            assert config.input_size == size

    def test_pretrained_config(self):
        config = YOLOModelConfig(
            arch="m",
            input_size=832,
            num_classes=2,
            class_names={0: "business_card", 1: "logo"},
            pretrained=True,
        )
        assert config.arch == "m"
        assert config.input_size == 832
        assert config.num_classes == 2
        assert config.class_names[1] == "logo"
        assert config.pretrained

    def test_to_dict(self):
        config = YOLOModelConfig(arch="s", input_size=416)
        d = config.to_dict()
        assert d["arch"] == "s"
        assert d["input_size"] == 416
        assert isinstance(d["freeze"], dict)
        assert isinstance(d["nms"], dict)
        assert isinstance(d["augmentation"], dict)

    def test_from_dict(self):
        data = {
            "arch": "l",
            "input_size": 960,
            "num_classes": 3,
            "pretrained": True,
            "freeze": {"backbone": True},
            "nms": {"conf_threshold": 0.5},
            "augmentation": {"mosaic": 0.5},
        }
        config = YOLOModelConfig.from_dict(data)
        assert config.arch == "l"
        assert config.input_size == 960
        assert config.num_classes == 3
        assert config.pretrained
        assert config.freeze.backbone
        assert config.nms.conf_threshold == 0.5
        assert config.augmentation.mosaic == 0.5

    def test_from_dict_ignores_extra_keys(self):
        data = {"arch": "x", "input_size": 1280, "unknown_key": "ignored"}
        config = YOLOModelConfig.from_dict(data)
        assert config.arch == "x"
        assert not hasattr(config, "unknown_key")


class TestYOLONMSConfig:
    def test_defaults(self):
        cfg = YOLONMSConfig()
        assert cfg.conf_threshold == 0.25
        assert cfg.iou_threshold == 0.45
        assert cfg.max_detections == 300
        assert not cfg.agnostic_nms

    def test_to_dict(self):
        cfg = YOLONMSConfig(conf_threshold=0.5, iou_threshold=0.6)
        d = cfg.to_dict()
        assert d["conf_threshold"] == 0.5
        assert d["iou_threshold"] == 0.6

    def test_from_dict(self):
        cfg = YOLONMSConfig.from_dict({"conf_threshold": 0.8, "max_detections": 100})
        assert cfg.conf_threshold == 0.8
        assert cfg.max_detections == 100
        assert cfg.iou_threshold == 0.45  # default


class TestYOLOAugmentationConfig:
    def test_defaults(self):
        cfg = YOLOAugmentationConfig()
        assert cfg.mosaic == 1.0
        assert cfg.mixup == 0.1
        assert cfg.auto_augment == "randaugment"

    def test_to_from_dict(self):
        cfg = YOLOAugmentationConfig(mosaic=0.0, mixup=0.5)
        d = cfg.to_dict()
        restored = YOLOAugmentationConfig.from_dict(d)
        assert restored.mosaic == 0.0
        assert restored.mixup == 0.5


class TestYOLOFreezeConfig:
    def test_defaults(self):
        cfg = YOLOFreezeConfig()
        assert not cfg.backbone
        assert cfg.exclude == ["dfl", "cls", "reg"]

    def test_freeze_backbone(self):
        cfg = YOLOFreezeConfig(backbone=True)
        assert cfg.backbone
        assert not cfg.neck
        assert not cfg.head

    def test_to_from_dict(self):
        cfg = YOLOFreezeConfig(backbone=True, neck=True, layers=[0, 1, 2])
        d = cfg.to_dict()
        restored = YOLOFreezeConfig.from_dict(d)
        assert restored.backbone
        assert restored.neck
        assert not restored.head
        assert restored.layers == [0, 1, 2]
