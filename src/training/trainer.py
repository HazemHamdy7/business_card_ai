from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .callbacks import CallbackHandler, CallbackEvent
from .checkpoint_manager import CheckpointManager
from .dataset_loader import DatasetLoader, DatasetInfo
from .device_manager import DeviceManager
from .experiment_tracker import ExperimentTracker
from .seed_manager import SeedManager
from .training_config import TrainingConfig
from .training_metrics import TrainingMetrics


class Trainer(ABC):
    def __init__(
        self,
        config: TrainingConfig,
        device_manager: DeviceManager,
        seed_manager: SeedManager,
        checkpoint_manager: CheckpointManager,
        experiment_tracker: ExperimentTracker,
        metrics: TrainingMetrics,
        callback_handler: CallbackHandler,
    ):
        self.config = config
        self.device_manager = device_manager
        self.seed_manager = seed_manager
        self.checkpoint_manager = checkpoint_manager
        self.experiment_tracker = experiment_tracker
        self.metrics = metrics
        self.callback_handler = callback_handler

    @abstractmethod
    def train(self) -> Dict[str, Any]:
        raise NotImplementedError(
            "Trainer is a base class. "
            "Use a concrete implementation (e.g., YOLOTrainer) to train models."
        )

    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        raise NotImplementedError(
            "Validation is not implemented in the base Trainer class."
        )

    @abstractmethod
    def predict(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(
            "Prediction is not implemented in the base Trainer class."
        )

    def _invoke_callbacks(
        self, event: CallbackEvent, context: Optional[Dict[str, Any]] = None
    ) -> None:
        self.callback_handler.invoke(event, context or {})

    def prepare(self) -> None:
        pass

    def cleanup(self) -> None:
        pass
