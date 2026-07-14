import tempfile
import pytest

from src.training import TrainingSession, TrainingConfig
from src.training.checkpoint_manager import CheckpointManager
from src.training.experiment_tracker import ExperimentTracker


class TestTrainingStress:
    @classmethod
    def setup_class(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()

    @classmethod
    def teardown_class(cls):
        cls.tmpdir.cleanup()

    def test_many_checkpoints(self):
        manager = CheckpointManager(
            save_dir=self.tmpdir.name + "/stress_ckpt",
            max_checkpoints=100,
            keep_last=True,
        )
        for i in range(100):
            manager.save({"epoch": i}, epoch=i + 1, score=float(i) / 100)
        ckpts = manager.list_checkpoints()
        assert len(ckpts) >= 1

    def test_many_experiments(self):
        tracker = ExperimentTracker(
            output_dir=self.tmpdir.name + "/stress_exp",
        )
        for i in range(50):
            eid = f"stress_exp_{i}"
            tracker.create_experiment(eid)
            tracker.start_experiment(eid)
            for epoch in range(3):
                tracker.log_epoch(eid, epoch=epoch + 1, loss=0.5 / (epoch + 1))
            tracker.complete_experiment(eid)
        experiments = tracker.list_experiments()
        assert len(experiments) == 50

    def test_repeated_session_runs(self):
        for i in range(5):
            tmp = tempfile.TemporaryDirectory()
            config = TrainingConfig(
                output_dir=tmp.name + "/output",
                save_dir=tmp.name + "/ckpt",
                epochs=2,
            )
            session = TrainingSession(config=config)
            result = session.run()
            assert result["status"] == "completed"
            tmp.cleanup()
