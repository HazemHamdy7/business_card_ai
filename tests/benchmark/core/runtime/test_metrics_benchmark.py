import time

from src.core.runtime.metrics import Counter, Histogram, MetricRegistry, Timer


class TestMetricsBenchmark:
    def test_counter_increment_speed(self) -> None:
        c = Counter("bench")
        start = time.perf_counter()
        iterations = 200000
        for _ in range(iterations):
            c.increment()
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 100000

    def test_histogram_observe_speed(self) -> None:
        h = Histogram("bench")
        start = time.perf_counter()
        iterations = 50000
        for i in range(iterations):
            h.observe(i / 1000.0)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 10000

    def test_timer_context_speed(self) -> None:
        from src.core.runtime.metrics import Timer
        t = Timer("bench")
        start = time.perf_counter()
        iterations = 1000
        for _ in range(iterations):
            with t.time():
                pass
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 100
