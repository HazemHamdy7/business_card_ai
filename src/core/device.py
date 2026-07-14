from __future__ import annotations

import platform
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DeviceInfo:
    device_type: str = "cpu"
    device_name: str = ""
    cuda_available: bool = False
    cuda_version: Optional[str] = None
    cuda_device_count: int = 0
    cuda_device_name: Optional[str] = None
    cuda_compute_capability: Optional[str] = None
    mps_available: bool = False
    memory_total_mb: Optional[float] = None
    memory_free_mb: Optional[float] = None
    memory_used_mb: Optional[float] = None
    cpu_count: int = 0
    cpu_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_type": self.device_type,
            "device_name": self.device_name,
            "cuda_available": self.cuda_available,
            "cuda_version": self.cuda_version,
            "cuda_device_count": self.cuda_device_count,
            "cuda_device_name": self.cuda_device_name,
            "cuda_compute_capability": self.cuda_compute_capability,
            "mps_available": self.mps_available,
            "memory_total_mb": self.memory_total_mb,
            "memory_free_mb": self.memory_free_mb,
            "memory_used_mb": self.memory_used_mb,
            "cpu_count": self.cpu_count,
            "cpu_name": self.cpu_name,
        }


def get_device_info() -> DeviceInfo:
    info = DeviceInfo()
    info.cpu_count = _get_cpu_count()
    info.cpu_name = _get_cpu_name()

    try:
        import torch
        info.cuda_available = torch.cuda.is_available()
        info.mps_available = (
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        )

        if info.cuda_available:
            info.device_type = "cuda"
            info.cuda_version = torch.version.cuda
            info.cuda_device_count = torch.cuda.device_count()
            if info.cuda_device_count > 0:
                info.cuda_device_name = torch.cuda.get_device_name(0)
                cap = torch.cuda.get_device_capability(0)
                info.cuda_compute_capability = f"{cap[0]}.{cap[1]}"
                info.device_name = info.cuda_device_name
                try:
                    info.memory_total_mb = (
                        torch.cuda.get_device_properties(0).total_mem / 1024 / 1024
                    )
                    free, used = _get_cuda_memory()
                    info.memory_free_mb = free
                    info.memory_used_mb = used
                except Exception:
                    pass
        elif info.mps_available:
            info.device_type = "mps"
            info.device_name = "Apple MPS"
        else:
            info.device_type = "cpu"
            info.device_name = _get_cpu_name()
    except ImportError:
        info.device_type = "cpu"
        info.device_name = _get_cpu_name()

    return info


def _get_cpu_count() -> int:
    try:
        import os
        return os.cpu_count() or 1
    except Exception:
        return 1


def _get_cpu_name() -> str:
    try:
        return platform.processor() or platform.machine()
    except Exception:
        return "unknown"


def _get_cuda_memory() -> tuple:
    try:
        import torch
        if torch.cuda.is_available():
            free, total = torch.cuda.mem_get_info()
            return free / 1024 / 1024, (total - free) / 1024 / 1024
    except Exception:
        pass
    return None, None
