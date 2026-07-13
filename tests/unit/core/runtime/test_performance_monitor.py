from src.core.runtime.performance_monitor import PerformanceMonitor


class TestPerformanceMonitor:
    def setup_method(self) -> None:
        self.monitor = PerformanceMonitor(window_size=10)

    def test_record_execution(self) -> None:
        self.monitor.record_execution(1.5)
        self.monitor.record_execution(2.5)
        assert self.monitor.avg_execution_time == 2.0
        assert self.monitor.min_execution_time == 1.5
        assert self.monitor.max_execution_time == 2.5

    def test_record_memory(self) -> None:
        self.monitor.record_memory()
        assert self.monitor.avg_memory_mb > 0

    def test_record_cpu(self) -> None:
        self.monitor.record_cpu()
        assert self.monitor.avg_cpu_percent >= 0

    def test_record_fps(self) -> None:
        self.monitor.record_fps(30.0)
        self.monitor.record_fps(60.0)
        assert self.monitor.avg_fps == 45.0

    def test_snapshot(self) -> None:
        self.monitor.record_execution(1.0)
        snap = self.monitor.snapshot()
        assert snap.execution_time == 1.0

    def test_reset(self) -> None:
        self.monitor.record_execution(1.0)
        self.monitor.reset()
        assert self.monitor.avg_execution_time == 0.0

    def test_to_dict(self) -> None:
        self.monitor.record_execution(1.0)
        d = self.monitor.to_dict()
        assert "current" in d
        assert "avg_execution_time" in d
