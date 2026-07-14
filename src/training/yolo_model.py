from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from src.core.logger import get_core_logger

from .yolo_config import YOLOModelConfig


@dataclass
class YOLOModelInfo:
    model_id: str
    arch: str
    input_size: int
    num_classes: int
    class_names: Dict[int, str]
    pretrained: bool
    weight_path: Optional[str] = None
    param_count: int = 0
    flops: int = 0
    layers: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


ARCH_SCALE: Dict[str, Dict[str, float]] = {
    "n": {"depth": 0.33, "width": 0.25, "max_channels": 1024},
    "s": {"depth": 0.33, "width": 0.50, "max_channels": 1024},
    "m": {"depth": 0.67, "width": 0.75, "max_channels": 768},
    "l": {"depth": 1.00, "width": 1.00, "max_channels": 512},
    "x": {"depth": 1.00, "width": 1.25, "max_channels": 512},
}


class YOLOModel:
    def __init__(self, config: YOLOModelConfig):
        self.config = config
        self.logger = get_core_logger()
        self._model: Any = None
        self._info: Optional[YOLOModelInfo] = None

    @property
    def model(self) -> Any:
        return self._model

    @property
    def info(self) -> Optional[YOLOModelInfo]:
        return self._info

    def build(self) -> YOLOModelInfo:
        scale = ARCH_SCALE.get(self.config.arch, ARCH_SCALE["n"])
        compute_layers = max(3, int(9 * scale["depth"]))
        compute_channels = max(16, int(64 * scale["width"]))

        self._info = YOLOModelInfo(
            model_id=f"yolo{self.config.arch}_business_card",
            arch=self.config.arch,
            input_size=self.config.input_size,
            num_classes=self.config.num_classes,
            class_names=self.config.class_names,
            pretrained=self.config.pretrained,
            weight_path=self.config.pretrained_weights,
            param_count=0,
            flops=0,
            layers=compute_layers,
            metadata={
                "scale_factors": scale,
                "base_channels": compute_channels,
                "multi_scale": self.config.multi_scale,
                "amp": self.config.amp,
                "cache_images": self.config.cache_images,
                "rect_training": self.config.rect_training,
            },
        )

        self._model = None
        self.logger.info(
            f"YOLO{self.config.arch} model configured",
            extra={
                "input_size": self.config.input_size,
                "num_classes": self.config.num_classes,
                "pretrained": self.config.pretrained,
                "layers": compute_layers,
            },
        )
        return self._info

    def load_weights(self, path: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Weight file not found: {path}")
        if self._info:
            self._info.weight_path = path
            self._info.pretrained = True
        self.logger.info(f"Weights staged for loading: {path}")

    def get_expected_input_shape(self) -> tuple:
        return (1, 3, self.config.input_size, self.config.input_size)

    def summary(self) -> Dict[str, Any]:
        if self._info:
            return self._info.to_dict()
        return {"status": "not_built"}

    def get_freeze_layers(self) -> List[str]:
        frozen: List[str] = []
        fc = self.config.freeze
        if fc.backbone:
            frozen.append("backbone")
        if fc.neck:
            frozen.append("neck")
        if fc.head:
            frozen.append("head")
        if fc.layers:
            frozen.extend([str(l) for l in fc.layers])
        return frozen
