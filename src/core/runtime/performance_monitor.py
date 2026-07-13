import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, TypeVar

from src.core.runtime.memory_monitor import MemoryMonitor
from src.core.runtime.gpu_monitor import GPUMonitor

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class PerformanceSnapshot:
    execution_time: float = 0.0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    gpu_percent: float = 0.0
    gpu_memory_mb: float = 0.0
    fps: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "execution_time": self.execution_time,
            "memory_mb": self.memory_mb,
            "cpu_percent": self.cpu_percent,
            "gpu_percent": self.gpu_percent,
            "gpu_memory_mb": self.gpu_memory_mb,
            "fps": self.fps,
        }


class PerformanceMonitor:
    def __init__(self, window_size: int = 100) -> None:
        self._window_size = window_size
        self._execution_times: list[float] = []
        self._memory_readings: list[float] = []
        self._cpu_readings: list[float] = []
        self._gpu_readings: list[float] = []
        self._gpu_memory_readings: list[float] = []
        self._fps_readings: list[float] = []
        self._memory_monitor = MemoryMonitor()
        self._gpu_monitor = GPUMonitor()
        self._lock = threading.Lock()

    def record_execution(self, seconds: float) -> None:
        with self._lock:
            self._execution_times.append(seconds)
            if len(self._execution_times) > self._window_size:
                self._execution_times.pop(0)

    def record_memory(self) -> None:
        snapshot = self._memory_monitor.snapshot()
        with self._lock:
            self._memory_readings.append(snapshot.rss_mb)
            if len(self._memory_readings) > self._window_size:
                self._memory_readings.pop(0)

    def record_cpu(self) -> None:
        snapshot = self._memory_monitor.snapshot()
        with self._lock:
            self._cpu_readings.append(snapshot.cpu_percent)
            if len(self._cpu_readings) > self._window_size:
                self._cpu_readings.pop(0)

    def record_gpu(self) -> None:
        snapshot = self._gpu_monitor.snapshot()
        with self._lock:
            self._gpu_readings.append(snapshot.gpu_percent)
            self._gpu_memory_readings.append(snapshot.memory_mb)
            if len(self._gpu_readings) > self._window_size:
                self._gpu_readings.pop(0)
                self._gpu_memory_readings.pop(0)

    def record_fps(self, fps: float) -> None:
        with self._lock:
            self._fps_readings.append(fps)
            if len(self._fps_readings) > self._window_size:
                self._fps_readings.pop(0)

    def snapshot(self) -> PerformanceSnapshot:
        mem = self._memory_monitor.snapshot()
        gpu = self._gpu_monitor.snapshot()
        with self._lock:
            return PerformanceSnapshot(
                execution_time=self._average(self._execution_times),
                memory_mb=mem.rss_mb,
                cpu_percent=mem.cpu_percent,
                gpu_percent=gpu.gpu_percent,
                gpu_memory_mb=gpu.memory_mb,
                fps=self._average(self._fps_readings),
            )

    @property
    def avg_execution_time(self) -> float:
        with self._lock:
            return self._average(self._execution_times)

    @property
    def min_execution_time(self) -> float:
        with self._lock:
            return self._min(self._execution_times)

    @property
    def max_execution_time(self) -> float:
        with self._lock:
            return self._max(self._execution_times)

    @property
    def avg_memory_mb(self) -> float:
        with self._lock:
            return self._average(self._memory_readings)

    @property
    def avg_cpu_percent(self) -> float:
        with self._lock:
            return self._average(self._cpu_readings)

    @property
    def avg_gpu_percent(self) -> float:
        with self._lock:
            return self._average(self._gpu_readings)

    @property
    def avg_fps(self) -> float:
        with self._lock:
            return self._average(self._fps_readings)

    def reset(self) -> None:
        with self._lock:
            self._execution_times.clear()
            self._memory_readings.clear()
            self._cpu_readings.clear()
            self._gpu_readings.clear()
            self._gpu_memory_readings.clear()
            self._fps_readings.clear()

    def to_dict(self) -> dict[str, Any]:
        snap = self.snapshot()
        return {
            "current": snap.to_dict(),
            "avg_execution_time": self.avg_execution_time,
            "min_execution_time": self.min_execution_time,
            "max_execution_time": self.max_execution_time,
            "avg_memory_mb": self.avg_memory_mb,
            "avg_cpu_percent": self.avg_cpu_percent,
            "avg_gpu_percent": self.avg_gpu_percent,
            "avg_fps": self.avg_fps,
            "sample_count": len(self._execution_times),
        }

    @staticmethod
    def _average(values: list[float]) -> float:
        return round(sum(values) / len(values), 4) if values else 0.0

    @staticmethod
    def _min(values: list[float]) -> float:
        return round(min(values), 4) if values else 0.0

    @staticmethod
    def _max(values: list[float]) -> float:
        return round(max(values), 4) if values else 0.0
