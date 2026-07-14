from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MetricsSnapshot:
    epoch: int = 0
    loss: float = 0.0
    learning_rate: float = 0.0
    epoch_time: float = 0.0
    gpu_utilization: Optional[float] = None
    memory_used_mb: Optional[float] = None
    eta_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "loss": self.loss,
            "learning_rate": self.learning_rate,
            "epoch_time": self.epoch_time,
            "gpu_utilization": self.gpu_utilization,
            "memory_used_mb": self.memory_used_mb,
            "eta_seconds": self.eta_seconds,
        }


class TrainingMetrics:
    def __init__(self, window_size: int = 10):
        self._window_size = window_size
        self._epoch_times: List[float] = []
        self._losses: List[float] = []
        self._learning_rates: List[float] = []
        self._snapshots: List[MetricsSnapshot] = []
        self._start_time: float = 0.0
        self._current_epoch_start: float = 0.0

    def start(self) -> None:
        self._start_time = time.perf_counter()
        self._epoch_times.clear()
        self._losses.clear()
        self._learning_rates.clear()
        self._snapshots.clear()

    def start_epoch(self) -> None:
        self._current_epoch_start = time.perf_counter()

    def end_epoch(
        self,
        epoch: int,
        loss: float,
        learning_rate: float,
    ) -> MetricsSnapshot:
        epoch_time = time.perf_counter() - self._current_epoch_start
        self._epoch_times.append(epoch_time)
        self._losses.append(loss)
        self._learning_rates.append(learning_rate)

        snapshot = MetricsSnapshot(
            epoch=epoch,
            loss=loss,
            learning_rate=learning_rate,
            epoch_time=epoch_time,
            gpu_utilization=self._get_gpu_utilization(),
            memory_used_mb=self._get_gpu_memory(),
            eta_seconds=self._compute_eta(),
        )
        self._snapshots.append(snapshot)
        return snapshot

    @property
    def moving_average_loss(self) -> float:
        if not self._losses:
            return 0.0
        window = self._losses[-self._window_size:]
        return sum(window) / len(window)

    @property
    def moving_average_lr(self) -> float:
        if not self._learning_rates:
            return 0.0
        window = self._learning_rates[-self._window_size:]
        return sum(window) / len(window)

    @property
    def average_epoch_time(self) -> float:
        if not self._epoch_times:
            return 0.0
        return sum(self._epoch_times) / len(self._epoch_times)

    @property
    def total_elapsed(self) -> float:
        if self._start_time == 0:
            return 0.0
        return time.perf_counter() - self._start_time

    @property
    def latest_snapshot(self) -> Optional[MetricsSnapshot]:
        return self._snapshots[-1] if self._snapshots else None

    def _compute_eta(self) -> float:
        if not self._epoch_times or not self._snapshots:
            return 0.0
        avg_time = self.average_epoch_time
        completed = len(self._snapshots)
        if completed == 0:
            return 0.0
        remaining = self._snapshots[0].epoch - completed
        return max(0.0, remaining * avg_time)

    def _get_gpu_utilization(self) -> Optional[float]:
        try:
            import torch
            if torch.cuda.is_available():
                return torch.cuda.utilization()
        except Exception:
            pass
        return None

    def _get_gpu_memory(self) -> Optional[float]:
        try:
            import torch
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024 / 1024
                return round(allocated, 2)
        except Exception:
            pass
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "moving_average_loss": self.moving_average_loss,
            "moving_average_lr": self.moving_average_lr,
            "average_epoch_time": self.average_epoch_time,
            "total_elapsed": self.total_elapsed,
            "total_epochs_completed": len(self._snapshots),
        }

    def get_snapshots(self) -> List[MetricsSnapshot]:
        return list(self._snapshots)
