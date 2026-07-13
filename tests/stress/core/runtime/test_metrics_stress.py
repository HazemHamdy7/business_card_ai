import threading

from src.core.runtime.metrics import MetricRegistry


class TestMetricsStress:
    def test_high_concurrency_counter(self) -> None:
        registry = MetricRegistry()
        errors: list[Exception] = []

        def worker() -> None:
            try:
                for _ in range(1000):
                    c = registry.counter("stress_counter")
                    c.increment()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
        assert registry.get_counter("stress_counter").value == 50000

    def test_histogram_many_observations(self) -> None:
        from src.core.runtime.metrics import Histogram
        h = Histogram("stress_histogram")
        for i in range(10000):
            h.observe(i / 1000.0)
        assert h.count == 10000
        assert h.avg > 0
