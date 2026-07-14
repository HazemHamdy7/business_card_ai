from __future__ import annotations

import platform
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.core.device import DeviceInfo, get_device_info


@dataclass
class DeviceCapability:
    device: str = "cpu"
    device_name: str = ""
    cuda_available: bool = False
    cuda_version: Optional[str] = None
    cuda_device_count: int = 0
    cuda_device_names: List[str] = field(default_factory=list)
    mps_available: bool = False
    memory_total_mb: float = 0.0
    memory_available_mb: float = 0.0
    cpu_count: int = 0
    supports_mixed_precision: bool = False
    max_batch_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device": self.device,
            "device_name": self.device_name,
            "cuda_available": self.cuda_available,
            "cuda_version": self.cuda_version,
            "cuda_device_count": self.cuda_device_count,
            "cuda_device_names": self.cuda_device_names,
            "mps_available": self.mps_available,
            "memory_total_mb": self.memory_total_mb,
            "memory_available_mb": self.memory_available_mb,
            "cpu_count": self.cpu_count,
            "supports_mixed_precision": self.supports_mixed_precision,
            "max_batch_size": self.max_batch_size,
        }


class DeviceManager:
    def __init__(self, device: str = "auto"):
        self._device_str = device
        self._device = None
        self._capability: Optional[DeviceCapability] = None
        self._resolve()

    def _resolve(self) -> None:
        info = get_device_info()
        cap = DeviceCapability()
        cap.cpu_count = info.cpu_count

        preferred = self._device_str.lower()

        if preferred == "cuda" or (preferred == "auto" and info.cuda_available):
            self._setup_cuda(cap, info)
        elif preferred == "mps" or (preferred == "auto" and info.mps_available):
            self._setup_mps(cap, info)
        elif preferred == "cpu":
            self._setup_cpu(cap, info)
        elif preferred == "auto":
            if info.cuda_available:
                self._setup_cuda(cap, info)
            elif info.mps_available:
                self._setup_mps(cap, info)
            else:
                self._setup_cpu(cap, info)
        else:
            self._setup_cpu(cap, info)

        self._capability = cap

    def _setup_cuda(self, cap: DeviceCapability, info: DeviceInfo) -> None:
        cap.device = "cuda"
        cap.device_name = info.cuda_device_name or "CUDA"
        cap.cuda_available = True
        cap.cuda_version = info.cuda_version
        cap.cuda_device_count = max(info.cuda_device_count, 1)
        cap.cuda_device_names = (
            [info.cuda_device_name] if info.cuda_device_name else []
        )
        if info.memory_total_mb:
            cap.memory_total_mb = info.memory_total_mb
            cap.memory_available_mb = info.memory_total_mb * 0.8
        else:
            cap.memory_total_mb = 8192
            cap.memory_available_mb = 6400
        cap.supports_mixed_precision = True
        cap.max_batch_size = self._estimate_batch_size(cap.memory_available_mb)

    def _setup_mps(self, cap: DeviceCapability, info: DeviceInfo) -> None:
        cap.device = "mps"
        cap.device_name = "Apple MPS"
        cap.mps_available = True
        cap.memory_total_mb = 8192
        cap.memory_available_mb = 6144
        cap.supports_mixed_precision = True
        cap.max_batch_size = self._estimate_batch_size(cap.memory_available_mb)

    def _setup_cpu(self, cap: DeviceCapability, info: DeviceInfo) -> None:
        cap.device = "cpu"
        cap.device_name = info.cpu_name or "CPU"
        cap.memory_total_mb = 16384
        cap.memory_available_mb = 8192
        cap.supports_mixed_precision = False
        cap.max_batch_size = self._estimate_batch_size(cap.memory_available_mb)

    def _estimate_batch_size(self, memory_mb: float) -> int:
        if memory_mb >= 32000:
            return 64
        elif memory_mb >= 16000:
            return 32
        elif memory_mb >= 8000:
            return 16
        elif memory_mb >= 4000:
            return 8
        else:
            return 4

    @property
    def device(self) -> str:
        return self._capability.device if self._capability else "cpu"

    @property
    def capability(self) -> DeviceCapability:
        if self._capability is None:
            self._resolve()
        return self._capability

    def to_torch_device(self):
        try:
            import torch
            if self.device == "cuda":
                return torch.device("cuda")
            elif self.device == "mps":
                return torch.device("mps")
            else:
                return torch.device("cpu")
        except ImportError:
            return None

    def get_device_info(self) -> DeviceInfo:
        return get_device_info()

    def summary(self) -> str:
        cap = self.capability
        lines = [
            f"Device: {cap.device}",
            f"Device Name: {cap.device_name}",
            f"CUDA: {cap.cuda_available} (v{cap.cuda_version or 'N/A'})",
            f"CUDA Devices: {cap.cuda_device_count}",
            f"MPS: {cap.mps_available}",
            f"Memory: {cap.memory_total_mb:.0f} MB",
            f"CPU Cores: {cap.cpu_count}",
            f"Mixed Precision: {cap.supports_mixed_precision}",
            f"Max Batch Size: {cap.max_batch_size}",
        ]
        return "\n".join(lines)
