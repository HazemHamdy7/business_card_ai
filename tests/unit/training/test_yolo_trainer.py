from __future__ import annotations

import pytest

from src.training.training_config import TrainingConfig
from src.training.device_manager import DeviceManager
from src.training.seed_manager import SeedManager
from src.training.checkpoint_manager import CheckpointManager
from src.training.experiment_tracker import ExperimentTracker
from src.training.training_metrics import TrainingMetrics
from src.training.callbacks import CallbackHandler, CallbackEvent
from src.training.yolo_config import YOLOModelConfig
from src.training.yolo_trainer import YOLOTrainer


@pytest.fixture
def trainer():
    config = TrainingConfig(epochs=3, batch_size=4)
    device_manager = DeviceManager(device="cpu")
    seed_manager = SeedManager(seed=42)
    checkpoint_manager = CheckpointManager(save_dir="test_checkpoints")
    experiment_tracker = ExperimentTracker(output_dir="test_experiments")
    metrics = TrainingMetrics()
    callback_handler = CallbackHandler()
    model_config = YOLOModelConfig(arch="n", input_size=640)
    return YOLOTrainer(
        config=config,
        device_manager=device_manager,
        seed_manager=seed_manager,
        checkpoint_manager=checkpoint_manager,
        experiment_tracker=experiment_tracker,
        metrics=metrics,
        callback_handler=callback_handler,
        model_config=model_config,
    )


class TestYOLOTrainer:
    def test_init(self, trainer):
        assert trainer.config.epochs == 3
        assert trainer.model_config.arch == "n"
        assert trainer.yolo_model is None
        assert trainer.model_info is None

    def test_prepare(self, trainer):
        trainer.prepare()
        assert trainer.yolo_model is not None
        assert trainer.model_info is not None
        assert trainer.model_info.arch == "n"
        assert trainer.model_info.input_size == 640

    def test_prepare_sets_model_info(self, trainer):
        trainer.prepare()
        info = trainer.model_info
        assert info.model_id == "yolon_business_card"
        assert info.num_classes == 1

    def test_prepare_with_pretrained_weights(self, tmp_path, trainer):
        weight_path = tmp_path / "yolo.pt"
        weight_path.write_text("dummy")
        trainer.model_config.pretrained_weights = str(weight_path)
        trainer.prepare()
        assert trainer.model_info
        assert trainer.model_info.weight_path == str(weight_path)

    def test_get_frozen_layers_default(self, trainer):
        trainer.prepare()
        assert trainer.get_frozen_layers() == []

    def test_get_frozen_layers_with_freeze(self, trainer):
        trainer.model_config.freeze.backbone = True
        trainer.prepare()
        frozen = trainer.get_frozen_layers()
        assert "backbone" in frozen

    def test_train_completes(self, trainer):
        trainer.prepare()
        result = trainer.train()
        assert result["status"] == "completed"
        assert result["arch"] == "n"
        assert result["epochs_completed"] > 0

    def test_train_raises_not_implemented_for_batch(self, trainer):
        trainer.prepare()
        with pytest.raises(NotImplementedError):
            trainer._train_batch(0)

    def test_validate_returns_dict(self, trainer):
        trainer.prepare()
        result = trainer.validate()
        assert "loss" in result
        assert "num_batches" in result
        assert result["status"] == "simulated"

    def test_predict_raises_not_implemented(self, trainer):
        trainer.prepare()
        with pytest.raises(NotImplementedError):
            trainer.predict()

    def test_summary(self, trainer):
        trainer.prepare()
        summary = trainer.summary()
        assert summary["model"] is not None
        assert summary["model"]["arch"] == "n"
        assert summary["frozen_layers"] == []
        assert summary["device"] == "cpu"

    def test_summary_before_prepare(self):
        config = TrainingConfig()
        trainer = YOLOTrainer(
            config=config,
            device_manager=DeviceManager(device="cpu"),
            seed_manager=SeedManager(),
            checkpoint_manager=CheckpointManager(save_dir="ckpt"),
            experiment_tracker=ExperimentTracker(output_dir="exp"),
            metrics=TrainingMetrics(),
            callback_handler=CallbackHandler(),
        )
        summary = trainer.summary()
        assert summary["model"] is None

    def test_train_uses_callbacks(self, trainer):
        events = []
        class TrackCallback:
            def on_training_start(self, ctx):
                events.append("start")
            def on_epoch_end(self, ctx):
                events.append(f"epoch_{ctx['epoch']}")
            def on_training_end(self, ctx):
                events.append("end")

        trainer.callback_handler.add(TrackCallback())
        trainer.prepare()
        trainer.train()
        assert "start" in events
        assert "end" in events
        assert any(e.startswith("epoch_") for e in events)

    def test_checkpoint_saved_on_best_loss(self, trainer):
        trainer.prepare()
        trainer.train()
        best = trainer.checkpoint_manager.get_best_score()
        assert best is not None

    def test_train_with_different_arch(self):
        config = TrainingConfig(epochs=2)
        trainer = YOLOTrainer(
            config=config,
            device_manager=DeviceManager(device="cpu"),
            seed_manager=SeedManager(),
            checkpoint_manager=CheckpointManager(save_dir="ckpt_x"),
            experiment_tracker=ExperimentTracker(output_dir="exp_x"),
            metrics=TrainingMetrics(),
            callback_handler=CallbackHandler(),
            model_config=YOLOModelConfig(arch="x", input_size=1280),
        )
        trainer.prepare()
        result = trainer.train()
        assert result["arch"] == "x"
