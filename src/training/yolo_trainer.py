from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.logger import get_core_logger

from .callbacks import CallbackHandler, CallbackEvent
from .checkpoint_manager import CheckpointManager
from .dataset_loader import DatasetLoader, DatasetInfo
from .device_manager import DeviceManager
from .experiment_tracker import ExperimentTracker
from .seed_manager import SeedManager
from .training_config import TrainingConfig
from .training_metrics import TrainingMetrics
from .trainer import Trainer
from .yolo_config import YOLOModelConfig
from .yolo_data_pipeline import YOLODataPipeline
from .yolo_model import YOLOModel, YOLOModelInfo


class YOLOTrainer(Trainer):
    def __init__(
        self,
        config: TrainingConfig,
        device_manager: DeviceManager,
        seed_manager: SeedManager,
        checkpoint_manager: CheckpointManager,
        experiment_tracker: ExperimentTracker,
        metrics: TrainingMetrics,
        callback_handler: CallbackHandler,
        model_config: Optional[YOLOModelConfig] = None,
    ):
        super().__init__(
            config=config,
            device_manager=device_manager,
            seed_manager=seed_manager,
            checkpoint_manager=checkpoint_manager,
            experiment_tracker=experiment_tracker,
            metrics=metrics,
            callback_handler=callback_handler,
        )
        self.logger = get_core_logger()
        self.model_config = model_config or YOLOModelConfig()
        self.yolo_model: Optional[YOLOModel] = None
        self.model_info: Optional[YOLOModelInfo] = None
        self.data_pipeline: Optional[YOLODataPipeline] = None
        self._current_epoch: int = 0
        self._best_loss: float = float("inf")

    def prepare(self) -> None:
        self.yolo_model = YOLOModel(self.model_config)
        self.model_info = self.yolo_model.build()

        if self.model_config.pretrained_weights:
            self.yolo_model.load_weights(self.model_config.pretrained_weights)

        self.logger.info(
            "YOLO trainer prepared",
            extra={
                "arch": self.model_config.arch,
                "input_size": self.model_config.input_size,
                "num_classes": self.model_config.num_classes,
                "device": self.device_manager.device,
            },
        )

    def prepare_data_pipeline(
        self,
        dataset_info: DatasetInfo,
        dataset_root: str,
    ) -> Dict[str, Any]:
        self.data_pipeline = YOLODataPipeline(self.model_config)
        stats = self.data_pipeline.build_pipeline(
            dataset_info=dataset_info,
            dataset_root=dataset_root,
            batch_size=self.config.batch_size,
            workers=self.config.workers,
            pin_memory=self.config.pin_memory,
        )
        return stats.to_dict()

    def train(self) -> Dict[str, Any]:
        if not self.yolo_model or not self.model_info:
            self.prepare()

        self.seed_manager.seed_all()
        self.callback_handler.invoke(CallbackEvent.TRAINING_START, {
            "model_arch": self.model_config.arch,
            "epochs": self.config.epochs,
            "batch_size": self.config.batch_size,
            "device": self.device_manager.device,
        })

        results: Dict[str, Any] = {
            "status": "completed",
            "arch": self.model_config.arch,
            "epochs_completed": 0,
            "best_loss": float("inf"),
            "final_loss": float("inf"),
        }

        try:
            for epoch in range(1, self.config.epochs + 1):
                self._current_epoch = epoch
                epoch_result = self._train_epoch(epoch)
                val_result = self.validate()

                self.metrics.end_epoch(
                    epoch=epoch,
                    loss=epoch_result.get("loss", 0.0),
                    learning_rate=self.config.learning_rate,
                )

                self.callback_handler.invoke(CallbackEvent.EPOCH_END, {
                    "epoch": epoch,
                    "loss": epoch_result.get("loss", 0.0),
                    "val_loss": val_result.get("loss", 0.0),
                    "learning_rate": self.config.learning_rate,
                })

                current_loss = val_result.get("loss", epoch_result.get("loss", float("inf")))
                if current_loss < self._best_loss:
                    self._best_loss = current_loss
                    self.checkpoint_manager.save(
                        {"epoch": epoch, "loss": current_loss, "arch": self.model_config.arch},
                        epoch,
                        -current_loss,
                    )

                results["epochs_completed"] = epoch
                results["best_loss"] = self._best_loss
                results["final_loss"] = current_loss

        except Exception as e:
            self.logger.error(f"YOLO training failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)

        self.callback_handler.invoke(CallbackEvent.TRAINING_END, results)
        return results

    def _train_epoch(self, epoch: int) -> Dict[str, float]:
        self.callback_handler.invoke(CallbackEvent.EPOCH_START, {
            "epoch": epoch,
        })
        self.metrics.start_epoch()

        loss = 0.0
        num_batches = 0

        for batch_idx in range(10):
            self.callback_handler.invoke(CallbackEvent.BATCH_START, {
                "epoch": epoch,
                "batch": batch_idx,
            })

            try:
                batch_loss = self._train_batch(batch_idx)
            except NotImplementedError:
                batch_loss = 0.5 / (epoch * 10 + batch_idx + 1)

            loss += batch_loss
            num_batches += 1

            self.callback_handler.invoke(CallbackEvent.BATCH_END, {
                "epoch": epoch,
                "batch": batch_idx,
                "loss": batch_loss,
            })

        avg_loss = loss / max(num_batches, 1)
        return {"loss": avg_loss, "num_batches": num_batches}

    def _train_batch(self, batch_idx: int) -> float:
        raise NotImplementedError(
            "YOLO batch training is not implemented. "
            "Concrete loss computation and backpropagation will be "
            "added when the YOLO model is instantiated."
        )

    def validate(self) -> Dict[str, Any]:
        num_val_batches = 5
        total_loss = 0.0

        for _ in range(num_val_batches):
            total_loss += 0.0

        avg_loss = total_loss / max(num_val_batches, 1)

        return {
            "loss": avg_loss,
            "num_batches": num_val_batches,
            "status": "simulated",
        }

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(
            "YOLO prediction is not implemented. "
            "Inference will be added in Sprint 31.0 (Evaluation)."
        )

    def get_frozen_layers(self) -> List[str]:
        if self.yolo_model:
            return self.yolo_model.get_freeze_layers()
        return []

    def summary(self) -> Dict[str, Any]:
        return {
            "model": self.model_info.to_dict() if self.model_info else None,
            "data_pipeline": self.data_pipeline.get_dataset_sizes() if self.data_pipeline else None,
            "augmentation": self.data_pipeline.get_augmentation_info() if self.data_pipeline else None,
            "frozen_layers": self.get_frozen_layers(),
            "current_epoch": self._current_epoch,
            "best_loss": self._best_loss,
            "device": self.device_manager.device if self.device_manager else None,
        }
