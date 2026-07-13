from src.core.runtime.gpu_monitor import GPUMonitor


class TestGPUMonitor:
    def setup_method(self) -> None:
        self.monitor = GPUMonitor()

    def test_snapshot(self) -> None:
        snap = self.monitor.snapshot()
        assert snap.available is False or snap.available is True
        assert snap.gpu_percent >= 0

    def test_snapshot_to_dict(self) -> None:
        snap = self.monitor.snapshot()
        d = snap.to_dict()
        assert "available" in d
        assert "gpu_percent" in d
        assert "memory_mb" in d

    def test_is_available(self) -> None:
        assert isinstance(self.monitor.is_available, bool)
