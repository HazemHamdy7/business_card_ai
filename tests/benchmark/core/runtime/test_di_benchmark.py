import time

from src.core.runtime.dependency_container import DependencyContainer
from src.core.runtime.metrics import Counter, MetricRegistry


class _BenchService:
    def __init__(self) -> None:
        self.value = 42


class TestDIBenchmark:
    def test_singleton_resolution_speed(self) -> None:
        container = DependencyContainer()
        container.register_singleton(_BenchService)
        container.resolve(_BenchService)
        start = time.perf_counter()
        iterations = 10000
        for _ in range(iterations):
            container.resolve(_BenchService)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 1000

    def test_transient_resolution_speed(self) -> None:
        container = DependencyContainer()
        container.register_transient(_BenchService)
        start = time.perf_counter()
        iterations = 1000
        for _ in range(iterations):
            container.resolve(_BenchService)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 100

    def test_metric_counter_speed(self) -> None:
        c = Counter("bench")
        start = time.perf_counter()
        iterations = 100000
        for _ in range(iterations):
            c.increment()
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 100000
