from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from src.core.constants import (
    DEFAULT_SEED,
    DEFAULT_BATCH_SIZE,
    DEFAULT_EPOCHS,
    DEFAULT_LEARNING_RATE,
    DEFAULT_WORKERS,
    DEFAULT_CHECKPOINT_INTERVAL,
    DEFAULT_LOG_INTERVAL,
    DEFAULT_WARMUP_EPOCHS,
    DEFAULT_PATIENCE,
    DEFAULT_GRADIENT_ACCUMULATION,
    DEFAULT_MIXED_PRECISION,
    DEFAULT_PIN_MEMORY,
    DEFAULT_IMAGE_SIZE,
)
from src.core.config import BaseConfig


@dataclass
class OptimizerConfig:
    name: str = "AdamW"
    lr: float = DEFAULT_LEARNING_RATE
    weight_decay: float = 0.0005
    momentum: float = 0.937
    eps: float = 1e-8
    betas: List[float] = field(default_factory=lambda: [0.9, 0.999])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OptimizerConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SchedulerConfig:
    name: str = "CosineAnnealingLR"
    warmup_epochs: int = DEFAULT_WARMUP_EPOCHS
    warmup_lr: float = 0.0001
    min_lr: float = 1e-6
    T_max: int = DEFAULT_EPOCHS
    eta_min: float = 1e-6
    factor: float = 0.5
    patience: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchedulerConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AugmentationConfig:
    mosaic: float = 1.0
    mixup: float = 0.0
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AugmentationConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TrainingConfig:
    project_name: str = "business_card_detection"
    experiment_name: str = "default"
    output_dir: str = "runs"

    batch_size: int = DEFAULT_BATCH_SIZE
    epochs: int = DEFAULT_EPOCHS
    workers: int = DEFAULT_WORKERS
    image_size: int = DEFAULT_IMAGE_SIZE

    learning_rate: float = DEFAULT_LEARNING_RATE
    weight_decay: float = 0.0005
    warmup_epochs: int = DEFAULT_WARMUP_EPOCHS
    patience: int = DEFAULT_PATIENCE
    early_stopping: bool = True
    early_stopping_delta: float = 0.001

    mixed_precision: bool = DEFAULT_MIXED_PRECISION
    gradient_accumulation: int = DEFAULT_GRADIENT_ACCUMULATION
    pin_memory: bool = DEFAULT_PIN_MEMORY

    seed: int = DEFAULT_SEED
    deterministic: bool = True
    benchmark: bool = False

    save_dir: str = "checkpoints"
    checkpoint_interval: int = DEFAULT_CHECKPOINT_INTERVAL
    log_interval: int = DEFAULT_LOG_INTERVAL
    save_best_only: bool = False
    max_checkpoints: int = 5
    keep_last: bool = True

    device: str = "auto"
    num_classes: int = 1
    class_names: Dict[int, str] = field(default_factory=lambda: {0: "business_card"})

    dataset_root: str = "dataset"
    train_image_dir: str = ""
    train_label_dir: str = ""
    val_image_dir: str = ""
    val_label_dir: str = ""
    test_image_dir: str = ""
    test_label_dir: str = ""
    dataset_format: str = "yolo"

    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    augmentation: AugmentationConfig = field(default_factory=AugmentationConfig)

    resume_path: Optional[str] = None
    pretrained_weights: Optional[str] = None
    freeze_backbone: bool = False

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in asdict(self).items():
            if key in ("optimizer", "scheduler", "augmentation"):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = dict(value)
            else:
                result[key] = value
        return result

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path

    @classmethod
    def load(cls, path: str) -> "TrainingConfig":
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingConfig":
        optimizer = data.pop("optimizer", None)
        scheduler = data.pop("scheduler", None)
        augmentation = data.pop("augmentation", None)
        if isinstance(optimizer, dict):
            data["optimizer"] = OptimizerConfig.from_dict(optimizer)
        if isinstance(scheduler, dict):
            data["scheduler"] = SchedulerConfig.from_dict(scheduler)
        if isinstance(augmentation, dict):
            data["augmentation"] = AugmentationConfig.from_dict(augmentation)
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    @classmethod
    def from_json(cls, path: str) -> "TrainingConfig":
        return cls.load(path)

    @classmethod
    def from_yaml(cls, path: str) -> "TrainingConfig":
        try:
            import yaml
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data or {})
        except ImportError:
            raise ImportError("PyYAML is required to load YAML config files")
        except FileNotFoundError:
            return cls()
