from src.core.runtime.memory_monitor import MemoryMonitor


class TestMemoryMonitor:
    def setup_method(self) -> None:
        self.monitor = MemoryMonitor()

    def test_snapshot(self) -> None:
        snap = self.monitor.snapshot()
        assert snap.rss_mb > 0
        assert snap.total_mb > 0
        assert snap.available_mb > 0

    def test_current_rss_mb(self) -> None:
        rss = self.monitor.current_rss_mb
        assert rss > 0

    def test_current_cpu_percent(self) -> None:
        cpu = self.monitor.current_cpu_percent
        assert cpu >= 0

    def test_snapshot_to_dict(self) -> None:
        snap = self.monitor.snapshot()
        d = snap.to_dict()
        assert "rss_mb" in d
        assert "vms_mb" in d
        assert "cpu_percent" in d
