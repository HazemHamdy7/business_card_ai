from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


DEFAULT_CONFIG = {
    "seed": None,
    "rotation": {
        "enabled": True,
        "angle_range": [-15, 15],
        "fixed_angle": None,
        "probability": 0.5,
    },
    "perspective": {
        "enabled": True,
        "strength": 0.05,
        "probability": 0.5,
    },
    "lighting": {
        "enabled": True,
        "brightness_range": [0.8, 1.2],
        "gamma_range": [0.8, 1.2],
        "exposure_range": [0.9, 1.1],
        "probability": 0.5,
    },
    "contrast": {
        "enabled": True,
        "alpha_range": [0.8, 1.2],
        "histogram_equalization": False,
        "probability": 0.5,
    },
    "blur": {
        "enabled": True,
        "gaussian_kernel_range": [3, 7],
        "motion_blur_kernel_range": [5, 15],
        "probability": 0.3,
    },
    "noise": {
        "enabled": True,
        "gaussian_std_range": [0.01, 0.03],
        "salt_pepper_amount_range": [0.01, 0.03],
        "probability": 0.3,
    },
    "color": {
        "enabled": True,
        "saturation_range": [0.8, 1.2],
        "hue_range": [-10, 10],
        "white_balance_range": [0.9, 1.1],
        "probability": 0.5,
    },
}


@dataclass
class AugmentationConfig:
    seed: Optional[int] = None
    rotation: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["rotation"]))
    perspective: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["perspective"]))
    lighting: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["lighting"]))
    contrast: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["contrast"]))
    blur: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["blur"]))
    noise: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["noise"]))
    color: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG["color"]))

    @classmethod
    def from_dict(cls, config: dict) -> "AugmentationConfig":
        merged = {}
        for key in DEFAULT_CONFIG:
            if key in config:
                if isinstance(DEFAULT_CONFIG[key], dict):
                    merged[key] = {**DEFAULT_CONFIG[key], **config[key]}
                else:
                    merged[key] = config[key]
            else:
                merged[key] = DEFAULT_CONFIG[key]
        return cls(**merged)

    @classmethod
    def from_yaml(cls, path: str) -> "AugmentationConfig":
        import yaml

        if not os.path.exists(path):
            return cls()
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        if data is None:
            return cls()
        return cls.from_dict(data)

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "rotation": dict(self.rotation),
            "perspective": dict(self.perspective),
            "lighting": dict(self.lighting),
            "contrast": dict(self.contrast),
            "blur": dict(self.blur),
            "noise": dict(self.noise),
            "color": dict(self.color),
        }

    def disable_all(self) -> "AugmentationConfig":
        for key in ["rotation", "perspective", "lighting", "contrast", "blur", "noise", "color"]:
            getattr(self, key)["enabled"] = False
        return self

    def enable_all(self) -> "AugmentationConfig":
        for key in ["rotation", "perspective", "lighting", "contrast", "blur", "noise", "color"]:
            getattr(self, key)["enabled"] = True
        return self

    def is_enabled(self, name: str) -> bool:
        cfg = getattr(self, name, None)
        if cfg is None:
            return False
        return cfg.get("enabled", True)
