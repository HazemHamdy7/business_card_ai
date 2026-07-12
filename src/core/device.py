import platform
import sys
from dataclasses import dataclass, field

import torch


@dataclass
class DeviceInfo:
    device_type: str = field(init=False)
    gpu_name: str | None = None
    pytorch_version: str = field(default_factory=lambda: torch.__version__)
    python_version: str = field(default_factory=lambda: sys.version.split()[0])
    operating_system: str = field(default_factory=lambda: f"{platform.system()} {platform.release()}")

    def __post_init__(self) -> None:
        if torch.cuda.is_available():
            self.device_type = "cuda"
            if self.gpu_name is None:
                try:
                    self.gpu_name = torch.cuda.get_device_name(0)
                except Exception:
                    self.gpu_name = None
        else:
            self.device_type = "cpu"
            self.gpu_name = None

    def is_cuda(self) -> bool:
        return self.device_type == "cuda"

    def is_cpu(self) -> bool:
        return self.device_type == "cpu"

    def to_dict(self) -> dict[str, str | None]:
        return {
            "device_type": self.device_type,
            "gpu_name": self.gpu_name,
            "pytorch_version": self.pytorch_version,
            "python_version": self.python_version,
            "operating_system": self.operating_system,
        }


def get_device() -> DeviceInfo:
    return DeviceInfo()
