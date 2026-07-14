import os
import tempfile
import pytest

from src.training import TrainingSession, TrainingConfig, DeviceManager, SeedManager
from src.training.checkpoint_manager import CheckpointManager
from src.training.experiment_tracker import ExperimentTracker
from src.training.model_registry import ModelRegistry
from src.training.dataset_loader import DatasetLoader


class TestTrainingIntegration:
    @pytest.fixture
    def workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = TrainingConfig(
                output_dir=os.path.join(tmp, "output"),
                save_dir=os.path.join(tmp, "checkpoints"),
                dataset_root=os.path.join(tmp, "dataset"),
                experiment_name="integration_test",
                epochs=3,
            )
            session = TrainingSession(config=config)
            yield session, tmp

    def test_full_session_lifecycle(self, workspace):
        session, tmp = workspace
        session.initialize()
        session.load_dataset()
        eid = session.start_experiment()

        tracker_record = session.experiment_tracker.get_record(eid)
        assert tracker_record is not None
        assert tracker_record.status == "running"

        result = session.run()
        assert result["status"] == "completed"

        record = session.experiment_tracker.get_record(eid)
        assert record.status == "completed"

    def test_device_and_seed_lifecycle(self, workspace):
        session, tmp = workspace
        dm = DeviceManager(device="cpu")
        sm = SeedManager(seed=42)

        assert dm.device == "cpu"
        assert sm.seed_all() == 42

        info = dm.get_device_info()
        assert info.cpu_count >= 1

    def test_checkpoint_and_experiment(self, workspace):
        session, tmp = workspace
        session.initialize()

        state = {"weights": [1, 2, 3], "epoch": 1}
        cp = session.checkpoint_manager.save(state, epoch=1, score=0.5)
        assert os.path.isfile(cp.path)

        eid = session.start_experiment()
        session.experiment_tracker.log_epoch(eid, epoch=1, loss=0.5)
        session.experiment_tracker.complete_experiment(eid)

        md = session.experiment_tracker.generate_markdown(eid)
        assert "completed" in md

    def test_model_registry_and_checkpoint(self, workspace):
        session, tmp = workspace
        session.initialize()

        entry = session.model_registry.register(
            "yolo_v8_test", "yolo",
            metadata={"framework": "ultralytics"},
        )
        assert entry.status == "registered"

        state = {"model": "test"}
        session.model_registry.save_model("yolo_v8_test", state)
        loaded = session.model_registry.load_model("yolo_v8_test")
        assert loaded["model"] == "test"

    def test_dataset_loader_with_real_files(self, workspace):
        session, tmp = workspace

        os.makedirs(os.path.join(tmp, "dataset", "train", "images"))
        os.makedirs(os.path.join(tmp, "dataset", "train", "labels"))
        with open(os.path.join(tmp, "dataset", "train", "images", "img001.jpg"), "w"):
            pass
        with open(os.path.join(tmp, "dataset", "train", "labels", "img001.txt"), "w") as f:
            f.write("0 0.5 0.5 0.4 0.6\n")

        loader = DatasetLoader()
        info = loader.load(os.path.join(tmp, "dataset"), format="yolo")
        assert info.train_images == 1
        assert info.train_labels == 1
        issues = loader.validate(info)
        assert len(issues) == 0
