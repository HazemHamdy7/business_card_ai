import os
import tempfile
import pytest

from src.training.experiment_tracker import ExperimentTracker, ExperimentRecord


class TestExperimentTracker:
    @pytest.fixture
    def tracker(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield ExperimentTracker(output_dir=tmp)

    def test_create_experiment(self, tracker):
        record = tracker.create_experiment("exp_001", config={"lr": 0.01})
        assert record.experiment_id == "exp_001"
        assert record.status == "created"
        assert record.config["lr"] == 0.01

    def test_start_experiment(self, tracker):
        tracker.create_experiment("exp_001")
        tracker.start_experiment("exp_001")
        record = tracker.get_record("exp_001")
        assert record.status == "running"

    def test_complete_experiment(self, tracker):
        tracker.create_experiment("exp_001")
        tracker.complete_experiment("exp_001", execution_time=120.5, best_score=0.95)
        record = tracker.get_record("exp_001")
        assert record.status == "completed"
        assert record.execution_time_seconds == 120.5
        assert record.best_score == 0.95

    def test_fail_experiment(self, tracker):
        tracker.create_experiment("exp_001")
        tracker.fail_experiment("exp_001", error="OOM")
        record = tracker.get_record("exp_001")
        assert record.status == "failed"
        assert "OOM" in record.notes

    def test_log_epoch(self, tracker):
        tracker.create_experiment("exp_001")
        tracker.log_epoch("exp_001", epoch=1, loss=0.5, metrics={"acc": 0.8})
        record = tracker.get_record("exp_001")
        assert record.loss_history == [0.5]
        assert record.metrics_history["acc"] == [0.8]
        assert record.completed_epochs == 1

    def test_list_experiments(self, tracker):
        tracker.create_experiment("exp_001")
        tracker.create_experiment("exp_002")
        experiments = tracker.list_experiments()
        assert len(experiments) == 2

    def test_record_to_dict(self):
        record = ExperimentRecord(experiment_id="test", status="completed")
        d = record.to_dict()
        assert d["experiment_id"] == "test"

    def test_record_to_summary(self):
        record = ExperimentRecord(
            experiment_id="test", status="completed",
            total_epochs=100, completed_epochs=50, best_score=0.9,
            execution_time_seconds=3600,
        )
        s = record.to_summary()
        assert s["best_score"] == 0.9

    def test_get_record_nonexistent(self, tracker):
        assert tracker.get_record("nonexistent") is None

    def test_generate_markdown(self, tracker):
        tracker.create_experiment("exp_001", config={"lr": 0.01})
        md = tracker.generate_markdown("exp_001")
        assert "Experiment: exp_001" in md
        assert "created" in md.lower()

    def test_hardware_tracking(self, tracker):
        tracker.create_experiment("exp_001")
        record = tracker.get_record("exp_001")
        record.hardware = {"device": "cpu", "cpu_count": 8}
        md = tracker.generate_markdown("exp_001")
        assert "cpu" in md
