import time
import pytest

from src.training.training_metrics import TrainingMetrics, MetricsSnapshot


class TestTrainingMetrics:
    @pytest.fixture
    def metrics(self):
        m = TrainingMetrics(window_size=3)
        m.start()
        return m

    def test_start(self, metrics):
        assert metrics.total_elapsed >= 0

    def test_end_epoch(self, metrics):
        metrics.start_epoch()
        time.sleep(0.01)
        snapshot = metrics.end_epoch(epoch=1, loss=0.5, learning_rate=0.001)
        assert isinstance(snapshot, MetricsSnapshot)
        assert snapshot.epoch == 1
        assert snapshot.loss == 0.5
        assert snapshot.learning_rate == 0.001
        assert snapshot.epoch_time > 0

    def test_moving_average_loss(self, metrics):
        for i in range(5):
            metrics.start_epoch()
            metrics.end_epoch(epoch=i + 1, loss=float(i), learning_rate=0.001)
        avg = metrics.moving_average_loss
        assert avg > 0

    def test_moving_average_lr(self, metrics):
        for i in range(5):
            metrics.start_epoch()
            metrics.end_epoch(epoch=i + 1, loss=0.5, learning_rate=0.001)
        assert metrics.moving_average_lr == 0.001

    def test_average_epoch_time(self, metrics):
        for i in range(3):
            metrics.start_epoch()
            time.sleep(0.01)
            metrics.end_epoch(epoch=i + 1, loss=0.5, learning_rate=0.001)
        assert metrics.average_epoch_time > 0

    def test_latest_snapshot(self, metrics):
        metrics.start_epoch()
        metrics.end_epoch(epoch=1, loss=0.5, learning_rate=0.001)
        snap = metrics.latest_snapshot
        assert snap is not None
        assert snap.epoch == 1

    def test_get_snapshots(self, metrics):
        for i in range(3):
            metrics.start_epoch()
            metrics.end_epoch(epoch=i + 1, loss=0.5, learning_rate=0.001)
        snapshots = metrics.get_snapshots()
        assert len(snapshots) == 3

    def test_to_dict(self, metrics):
        for i in range(3):
            metrics.start_epoch()
            metrics.end_epoch(epoch=i + 1, loss=0.5, learning_rate=0.001)
        d = metrics.to_dict()
        assert "moving_average_loss" in d
        assert "total_epochs_completed" in d

    def test_snapshot_to_dict(self):
        snap = MetricsSnapshot(epoch=1, loss=0.5, learning_rate=0.001, epoch_time=1.0)
        d = snap.to_dict()
        assert d["epoch"] == 1
        assert d["loss"] == 0.5

    def test_consecutive_epochs(self, metrics):
        for epoch, loss in [(1, 0.8), (2, 0.6), (3, 0.4)]:
            metrics.start_epoch()
            metrics.end_epoch(epoch=epoch, loss=loss, learning_rate=0.001)
        assert metrics.moving_average_loss < 0.8
