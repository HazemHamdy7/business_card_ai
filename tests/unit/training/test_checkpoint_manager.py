import os
import tempfile
import pytest

from src.training.checkpoint_manager import CheckpointManager, Checkpoint, torch_save, torch_load


class TestCheckpointManager:
    @pytest.fixture
    def manager(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield CheckpointManager(save_dir=tmp, max_checkpoints=3, keep_last=True)

    def test_save_checkpoint(self, manager):
        state = {"model": "test", "epoch": 1}
        cp = manager.save(state, epoch=1, score=0.5)
        assert cp.epoch == 1
        assert cp.score == 0.5
        assert os.path.isfile(cp.path)

    def test_load_checkpoint(self, manager):
        state = {"model": "test", "epoch": 1}
        manager.save(state, epoch=1, score=0.5)
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) >= 1
        loaded = manager.load(checkpoints[0].path)
        assert loaded is not None
        assert loaded["epoch"] == 1

    def test_best_checkpoint(self, manager):
        manager.save({"e": 1}, epoch=1, score=0.5)
        manager.save({"e": 2}, epoch=2, score=0.8)
        best_path = manager.get_best_path()
        assert best_path is not None
        assert os.path.isfile(best_path)

    def test_best_score(self, manager):
        manager.save({"e": 1}, epoch=1, score=0.5)
        manager.save({"e": 2}, epoch=2, score=0.8)
        assert manager.get_best_score() == 0.8

    def test_load_best(self, manager):
        manager.save({"e": 1}, epoch=1, score=0.5)
        manager.save({"e": 2}, epoch=2, score=0.8)
        loaded = manager.load_best()
        assert loaded is not None
        assert loaded["epoch"] == 2

    def test_summary(self, manager):
        manager.save({"e": 1}, epoch=1, score=0.5)
        summary = manager.summary()
        assert summary["total_checkpoints"] >= 1
        assert summary["max_checkpoints"] == 3

    def test_checkpoint_to_dict(self):
        cp = Checkpoint(path="/tmp/test.pt", epoch=1, score=0.5, timestamp="now")
        d = cp.to_dict()
        assert d["epoch"] == 1
        assert d["score"] == 0.5

    def test_torch_save_load(self):
        data = {"key": "value", "nested": {"a": 1}}
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
            path = f.name
        try:
            torch_save(data, path)
            loaded = torch_load(path)
            assert loaded["key"] == "value"
            assert loaded["nested"]["a"] == 1
        finally:
            if os.path.exists(path):
                os.unlink(path)
