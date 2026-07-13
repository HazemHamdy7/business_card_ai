from dataclasses import dataclass, field
from typing import Any

import torch


@dataclass
class GPUSnapshot:
    available: bool = False
    gpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_total_mb: float = 0.0
    memory_free_mb: float = 0.0
    temperature_c: float | None = None
    device_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "gpu_percent": self.gpu_percent,
            "memory_mb": self.memory_mb,
            "memory_total_mb": self.memory_total_mb,
            "memory_free_mb": self.memory_free_mb,
            "temperature_c": self.temperature_c,
            "device_name": self.device_name,
        }


class GPUMonitor:
    def __init__(self, device_id: int = 0) -> None:
        self._device_id = device_id
        self._available = torch.cuda.is_available()

    def snapshot(self) -> GPUSnapshot:
        if not self._available:
            return GPUSnapshot(available=False)

        try:
            gpu_percent = 0.0
            memory_used = torch.cuda.memory_allocated(self._device_id)
            memory_reserved = torch.cuda.memory_reserved(self._device_id)
            memory_total = torch.cuda.get_device_properties(self._device_id).total_memory
            memory_free = memory_total - memory_used
            device_name = torch.cuda.get_device_name(self._device_id)

            return GPUSnapshot(
                available=True,
                gpu_percent=round((memory_used / memory_total) * 100, 2) if memory_total > 0 else 0.0,
                memory_mb=round(memory_used / (1024 * 1024), 2),
                memory_total_mb=round(memory_total / (1024 * 1024), 2),
                memory_free_mb=round(memory_free / (1024 * 1024), 2),
                device_name=device_name,
            )
        except Exception:
            return GPUSnapshot(available=False)

    @property
    def is_available(self) -> bool:
        return self._available
