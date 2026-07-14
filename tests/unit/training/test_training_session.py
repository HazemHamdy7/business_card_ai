import os
import tempfile
import pytest

from src.training import TrainingSession, TrainingConfig
from src.training.callbacks import Callback, CallbackEvent
from src.training.trainer import Trainer


class TestTrainingSession:
    @pytest.fixture
    def session(self, tmpdir):
        config = TrainingConfig(
            output_dir=str(tmpdir / "output"),
            save_dir=str(tmpdir / "checkpoints"),
            dataset_root=str(tmpdir / "dataset"),
            epochs=5,
            batch_size=2,
        )
        return TrainingSession(config=config)

    def test_initialize(self, session):
        session.initialize()
        assert session._initialized

    def test_device(self, session):
        session.initialize()
        assert session.device_manager.device in ("cpu", "cuda", "mps")

    def test_seed(self, session):
        session.initialize()
        assert session.seed_manager.seed == 42

    def test_load_dataset_empty(self, session):
        info = session.load_dataset()
        assert info.total_images == 0
        assert info.total_labels == 0

    def test_run_no_trainer(self, session):
        session.initialize()
        result = session.run()
        assert result["status"] == "completed"
        assert "experiment_id" in result

    def test_run_with_callbacks(self, session):
        events = []

        class TestCallback(Callback):
            def on_training_start(self, context):
                events.append("start")
            def on_training_end(self, context):
                events.append("end")
            def on_epoch_end(self, context):
                events.append(f"epoch_{context.get('epoch')}")

        session.add_callback(TestCallback())
        result = session.run()
        assert "start" in events
        assert any(e.startswith("epoch_") for e in events)
        assert "end" in events
        assert result["status"] == "completed"

    def test_early_stopping(self, session):
        session.add_early_stopping()
        result = session.run()
        assert result["status"] == "completed"

    def test_summary(self, session):
        session.initialize()
        summary = session.summary()
        assert "config" in summary
        assert "device" in summary
        assert "dataset" in summary
        assert "experiments" in summary

    def test_experiment_id(self, session):
        session.initialize()
        eid = session.start_experiment()
        assert eid is not None
        assert session.config.experiment_name in eid

    def test_model_registry_available(self, session):
        session.initialize()
        entry = session.model_registry.register_future("yolo")
        assert entry is not None

    def test_checkpoint_manager_available(self, session):
        session.initialize()
        state = {"epoch": 1, "loss": 0.5}
        cp = session.checkpoint_manager.save(state, epoch=1, score=-0.5)
        assert cp is not None
        assert os.path.isfile(cp.path)
