from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.logger import get_core_logger

from .callbacks import (
    Callback,
    CallbackHandler,
    CallbackEvent,
    EarlyStoppingCallback,
    LoggingCallback,
)
from .checkpoint_manager import CheckpointManager
from .dataset_loader import DatasetLoader, DatasetInfo
from .device_manager import DeviceManager
from .experiment_tracker import ExperimentTracker
from .model_registry import ModelRegistry
from .seed_manager import SeedManager
from .training_config import TrainingConfig
from .training_metrics import TrainingMetrics
from .trainer import Trainer


class TrainingSession:
    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
    ):
        self.config = config or TrainingConfig()
        self.logger = get_core_logger()

        self.seed_manager = SeedManager(
            seed=self.config.seed,
            deterministic=self.config.deterministic,
        )
        self.device_manager = DeviceManager(device=self.config.device)
        self.checkpoint_manager = CheckpointManager(
            save_dir=self.config.save_dir,
            max_checkpoints=self.config.max_checkpoints,
            keep_last=self.config.keep_last,
            save_best_only=self.config.save_best_only,
        )
        self.experiment_tracker = ExperimentTracker(
            output_dir=os.path.join(self.config.output_dir, "experiments"),
        )
        self.model_registry = ModelRegistry(
            registry_dir=os.path.join(self.config.output_dir, "models"),
        )
        self.metrics = TrainingMetrics()
        self.callback_handler = CallbackHandler()
        self.dataset_loader = DatasetLoader()

        self._trainer: Optional[Trainer] = None
        self._dataset_info: Optional[DatasetInfo] = None
        self._experiment_id: Optional[str] = None
        self._start_time: float = 0.0
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        self.seed_manager.seed_all()
        self.logger.info(
            f"Training session initialized",
            extra={
                "device": self.device_manager.device,
                "seed": self.config.seed,
                "experiment": self.config.experiment_name,
            },
        )
        self._initialized = True

    def load_dataset(self) -> DatasetInfo:
        info = self.dataset_loader.load(
            dataset_root=self.config.dataset_root,
            format=self.config.dataset_format,
            train_image_dir=self.config.train_image_dir,
            train_label_dir=self.config.train_label_dir,
            val_image_dir=self.config.val_image_dir,
            val_label_dir=self.config.val_label_dir,
            test_image_dir=self.config.test_image_dir,
            test_label_dir=self.config.test_label_dir,
        )
        self._dataset_info = info

        issues = self.dataset_loader.validate(info)
        if issues:
            for issue in issues:
                self.logger.warning(f"Dataset issue: {issue}")

        self.logger.info(
            f"Dataset loaded: {info.total_images} images, "
            f"{info.total_labels} labels, format={info.format}"
        )
        return info

    def set_trainer(self, trainer: Trainer) -> None:
        self._trainer = trainer

    def add_callback(self, callback: Callback) -> None:
        self.callback_handler.add(callback)

    def add_early_stopping(self) -> EarlyStoppingCallback:
        cb = EarlyStoppingCallback(
            patience=self.config.patience,
            delta=self.config.early_stopping_delta,
        )
        self.callback_handler.add(cb)
        return cb

    def add_logging(self) -> LoggingCallback:
        cb = LoggingCallback(logger=self.logger)
        self.callback_handler.add(cb)
        return cb

    def start_experiment(self) -> str:
        self._experiment_id = (
            f"{self.config.experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        record = self.experiment_tracker.create_experiment(
            experiment_id=self._experiment_id,
            config=self.config.to_dict(),
            hyperparameters={
                "batch_size": self.config.batch_size,
                "learning_rate": self.config.learning_rate,
                "epochs": self.config.epochs,
                "optimizer": self.config.optimizer.name,
                "scheduler": self.config.scheduler.name,
            },
        )

        device_info = self.device_manager.get_device_info()
        record.hardware = device_info.to_dict()

        self.experiment_tracker.start_experiment(self._experiment_id)
        self._start_time = time.time()
        return self._experiment_id

    def run(self) -> Dict[str, Any]:
        self.initialize()

        if not self._dataset_info:
            self.load_dataset()

        experiment_id = self.start_experiment()
        self.metrics.start()

        context: Dict[str, Any] = {
            "config": self.config,
            "dataset_info": self._dataset_info,
            "experiment_id": experiment_id,
            "device": self.device_manager.device,
        }

        self.callback_handler.invoke(CallbackEvent.TRAINING_START, context)

        result: Dict[str, Any] = {"status": "completed"}

        try:
            if self._trainer:
                train_result = self._trainer.train()
                result.update(train_result)
            else:
                self.logger.warning(
                    "No trainer set. Session initialized with config only."
                )
                self._simulate_training(context)
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            self.experiment_tracker.fail_experiment(
                experiment_id, error=str(e)
            )
            context["error"] = str(e)
            self.callback_handler.invoke(CallbackEvent.EXCEPTION, context)
            result["status"] = "failed"
            result["error"] = str(e)
            return result

        execution_time = time.time() - self._start_time
        best_score = self.checkpoint_manager.get_best_score()

        self.experiment_tracker.complete_experiment(
            experiment_id,
            execution_time=execution_time,
            best_score=best_score,
        )

        context["execution_time"] = execution_time
        context["best_score"] = best_score
        self.callback_handler.invoke(CallbackEvent.TRAINING_END, context)

        result["experiment_id"] = experiment_id
        result["execution_time_seconds"] = execution_time
        result["best_score"] = best_score
        result["total_epochs_completed"] = len(self.metrics.get_snapshots())

        return result

    def _simulate_training(self, context: Dict[str, Any]) -> None:
        self.logger.info("Simulated training: no trainer set")
        for epoch in range(min(3, self.config.epochs)):
            epoch_context = {
                **context,
                "epoch": epoch + 1,
                "loss": 0.5 / (epoch + 1),
                "learning_rate": self.config.learning_rate,
            }
            self.callback_handler.invoke(CallbackEvent.EPOCH_START, epoch_context)

            self.metrics.start_epoch()

            loss = 0.5 / (epoch + 1)
            snapshot = self.metrics.end_epoch(
                epoch=epoch + 1,
                loss=loss,
                learning_rate=self.config.learning_rate,
            )

            epoch_context["loss"] = loss
            epoch_context["epoch_time"] = snapshot.epoch_time
            self.callback_handler.invoke(CallbackEvent.EPOCH_END, epoch_context)

            state = {"epoch": epoch + 1, "loss": loss}
            self.checkpoint_manager.save(state, epoch + 1, -loss)

            context = {**context, "loss": loss}
            self.callback_handler.invoke(
                CallbackEvent.CHECKPOINT_SAVED, context
            )

            if epoch_context.get("early_stop"):
                self.logger.info(
                    f"Early stopping triggered at epoch {epoch + 1}"
                )
                self.callback_handler.invoke(
                    CallbackEvent.EARLY_STOP, epoch_context
                )
                break

    def resume(self, checkpoint_path: str) -> Dict[str, Any]:
        state = self.checkpoint_manager.load(checkpoint_path)
        if state is None:
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        self.config.resume_path = checkpoint_path
        self.logger.info(
            f"Resuming from checkpoint: {checkpoint_path}",
            extra={"epoch": state.get("epoch", 0)},
        )
        return self.run()

    def summary(self) -> Dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "device": self.device_manager.capability.to_dict(),
            "dataset": self._dataset_info.to_dict() if self._dataset_info else None,
            "experiments": self.experiment_tracker.list_experiments(),
            "checkpoints": self.checkpoint_manager.summary(),
            "has_trainer": self._trainer is not None,
            "initialized": self._initialized,
        }
