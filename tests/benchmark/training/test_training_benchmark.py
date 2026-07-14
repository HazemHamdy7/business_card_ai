import time
import tempfile
import pytest

from src.training.checkpoint_manager import CheckpointManager


class TestTrainingBenchmark:
    @classmethod
    def setup_class(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()

    @classmethod
    def teardown_class(cls):
        cls.tmpdir.cleanup()

    def test_checkpoint_save_throughput(self):
        manager = CheckpointManager(
            save_dir=self.tmpdir.name + "/ckpt_bench",
            max_checkpoints=50,
        )
        iterations = 50
        start = time.perf_counter()
        for i in range(iterations):
            manager.save({"data": "x" * 1000}, epoch=i + 1, score=float(i) / 100)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 10

    def test_model_registry_throughput(self):
        from src.training.model_registry import ModelRegistry
        registry = ModelRegistry(registry_dir=self.tmpdir.name + "/reg_bench")
        iterations = 20
        start = time.perf_counter()
        for i in range(iterations):
            registry.register(f"model_{i}", "test")
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 10
