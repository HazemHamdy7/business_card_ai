from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


YOLO_ARCH_TYPES = ["n", "s", "m", "l", "x"]
YOLO_INPUT_SIZES = [320, 416, 512, 640, 736, 832, 960, 1024, 1280]


@dataclass
class YOLONMSConfig:
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_detections: int = 300
    agnostic_nms: bool = False
    max_time_per_image: float = 0.1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "YOLONMSConfig":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


@dataclass
class YOLOAugmentationConfig:
    mosaic: float = 1.0
    mixup: float = 0.1
    copy_paste: float = 0.0
    degrees: float = 0.0
    translate: float = 0.1
    scale: float = 0.5
    shear: float = 0.0
    perspective: float = 0.0
    flipud: float = 0.0
    fliplr: float = 0.5
    hsv_h: float = 0.015
    hsv_s: float = 0.7
    hsv_v: float = 0.4
    auto_augment: str = "randaugment"
    erasing: float = 0.4
    crop_fraction: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "YOLOAugmentationConfig":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


@dataclass
class YOLOFreezeConfig:
    backbone: bool = False
    neck: bool = False
    head: bool = False
    layers: List[int] = field(default_factory=list)
    exclude: List[str] = field(default_factory=lambda: ["dfl", "cls", "reg"])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "YOLOFreezeConfig":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


@dataclass
class YOLOModelConfig:
    arch: str = "n"
    input_size: int = 640
    pretrained: bool = False
    pretrained_weights: Optional[str] = None
    num_classes: int = 1
    class_names: Dict[int, str] = field(default_factory=lambda: {0: "business_card"})
    freeze: YOLOFreezeConfig = field(default_factory=YOLOFreezeConfig)
    nms: YOLONMSConfig = field(default_factory=YOLONMSConfig)
    augmentation: YOLOAugmentationConfig = field(default_factory=YOLOAugmentationConfig)
    multi_scale: bool = False
    multi_scale_range: List[int] = field(default_factory=lambda: [0.5, 1.5])
    amp: bool = True
    cache_images: bool = False
    rect_training: bool = False
    overlap_mask: bool = True

    def __post_init__(self) -> None:
        if self.arch not in YOLO_ARCH_TYPES:
            raise ValueError(
                f"Invalid YOLO architecture '{self.arch}'. "
                f"Must be one of {YOLO_ARCH_TYPES}"
            )
        if self.input_size not in YOLO_INPUT_SIZES:
            raise ValueError(
                f"Invalid input size {self.input_size}. "
                f"Must be one of {YOLO_INPUT_SIZES}"
            )
        if isinstance(self.freeze, dict):
            self.freeze = YOLOFreezeConfig(**self.freeze)
        if isinstance(self.nms, dict):
            self.nms = YOLONMSConfig(**self.nms)
        if isinstance(self.augmentation, dict):
            self.augmentation = YOLOAugmentationConfig(**self.augmentation)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in asdict(self).items():
            if key in ("freeze", "nms", "augmentation"):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = dict(value)
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "YOLOModelConfig":
        freeze = data.pop("freeze", None)
        nms = data.pop("nms", None)
        augmentation = data.pop("augmentation", None)
        if isinstance(freeze, dict):
            data["freeze"] = YOLOFreezeConfig.from_dict(freeze)
        if isinstance(nms, dict):
            data["nms"] = YOLONMSConfig.from_dict(nms)
        if isinstance(augmentation, dict):
            data["augmentation"] = YOLOAugmentationConfig.from_dict(augmentation)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)
