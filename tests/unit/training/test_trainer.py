import pytest

from src.training.trainer import Trainer
from src.training.training_config import TrainingConfig
from src.training.device_manager import DeviceManager
from src.training.seed_manager import SeedManager
from src.training.checkpoint_manager import CheckpointManager
from src.training.experiment_tracker import ExperimentTracker
from src.training.training_metrics import TrainingMetrics
from src.training.callbacks import CallbackHandler


class ConcreteTrainer(Trainer):
    def train(self):
        return {"status": "trained"}

    def validate(self):
        return {"status": "validated"}

    def predict(self, *args, **kwargs):
        return {"status": "predicted"}


class TestTrainer:
    @pytest.fixture
    def trainer(self, tmpdir):
        config = TrainingConfig(output_dir=str(tmpdir))
        device_manager = DeviceManager(device="cpu")
        seed_manager = SeedManager(seed=42)
        checkpoint_manager = CheckpointManager(save_dir=str(tmpdir / "checkpoints"))
        experiment_tracker = ExperimentTracker(output_dir=str(tmpdir / "experiments"))
        metrics = TrainingMetrics()
        callback_handler = CallbackHandler()
        return ConcreteTrainer(
            config=config,
            device_manager=device_manager,
            seed_manager=seed_manager,
            checkpoint_manager=checkpoint_manager,
            experiment_tracker=experiment_tracker,
            metrics=metrics,
            callback_handler=callback_handler,
        )

    def test_base_trainer_raises_not_implemented(self):
        with pytest.raises(TypeError):
            Trainer(config=TrainingConfig(), device_manager=DeviceManager(device="cpu"),
                     seed_manager=SeedManager(), checkpoint_manager=CheckpointManager(save_dir="tmp"),
                     experiment_tracker=ExperimentTracker(output_dir="tmp"),
                     metrics=TrainingMetrics(), callback_handler=CallbackHandler())

    def test_concrete_train(self, trainer):
        result = trainer.train()
        assert result["status"] == "trained"

    def test_concrete_validate(self, trainer):
        result = trainer.validate()
        assert result["status"] == "validated"

    def test_concrete_predict(self, trainer):
        result = trainer.predict("test")
        assert result["status"] == "predicted"
