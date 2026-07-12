import os
import platform
import sys
from dataclasses import dataclass, field
from typing import Any

import torch


def _get_gpu_name() -> str | None:
    if torch.cuda.is_available():
        try:
            return torch.cuda.get_device_name(0)
        except Exception:
            return None
    return None


@dataclass
class EnvironmentInfo:
    python_version: str = field(default_factory=lambda: sys.version.split()[0])
    operating_system: str = field(default_factory=lambda: f"{platform.system()} {platform.release()}")
    pytorch_version: str = field(default_factory=lambda: torch.__version__)
    cuda_available: bool = field(default_factory=lambda: torch.cuda.is_available())
    cuda_version: str | None = field(default_factory=lambda: torch.version.cuda if torch.cuda.is_available() else None)
    gpu_name: str | None = field(default_factory=_get_gpu_name)
    cpu_count: int = field(default_factory=lambda: os.cpu_count() or 1)
    is_ci: bool = field(default_factory=lambda: os.environ.get("CI", "").lower() in ("true", "1"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "python_version": self.python_version,
            "operating_system": self.operating_system,
            "pytorch_version": self.pytorch_version,
            "cuda_available": self.cuda_available,
            "cuda_version": self.cuda_version,
            "gpu_name": self.gpu_name,
            "cpu_count": self.cpu_count,
            "is_ci": self.is_ci,
        }


def get_environment_info() -> dict[str, Any]:
    return EnvironmentInfo().to_dict()
