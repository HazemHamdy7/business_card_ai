from dataclasses import dataclass

import psutil


@dataclass
class MemorySnapshot:
    rss_mb: float = 0.0
    vms_mb: float = 0.0
    percent: float = 0.0
    cpu_percent: float = 0.0
    available_mb: float = 0.0
    total_mb: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "rss_mb": self.rss_mb,
            "vms_mb": self.vms_mb,
            "percent": self.percent,
            "cpu_percent": self.cpu_percent,
            "available_mb": self.available_mb,
            "total_mb": self.total_mb,
        }


class MemoryMonitor:
    def __init__(self) -> None:
        self._process = psutil.Process()

    def snapshot(self) -> MemorySnapshot:
        mem = self._process.memory_info()
        cpu = self._process.cpu_percent(interval=0)
        system_mem = psutil.virtual_memory()
        return MemorySnapshot(
            rss_mb=round(mem.rss / (1024 * 1024), 2),
            vms_mb=round(mem.vms / (1024 * 1024), 2),
            percent=self._process.memory_percent(),
            cpu_percent=cpu,
            available_mb=round(system_mem.available / (1024 * 1024), 2),
            total_mb=round(system_mem.total / (1024 * 1024), 2),
        )

    @property
    def current_rss_mb(self) -> float:
        return self.snapshot().rss_mb

    @property
    def current_cpu_percent(self) -> float:
        return self.snapshot().cpu_percent
