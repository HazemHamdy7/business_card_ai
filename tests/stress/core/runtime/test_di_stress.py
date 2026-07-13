import threading

from src.core.runtime.dependency_container import DependencyContainer


class _StressService:
    def __init__(self) -> None:
        self.id = id(self)


class TestDIStress:
    def test_concurrent_resolution(self) -> None:
        container = DependencyContainer()
        container.register_singleton(_StressService)
        errors: list[Exception] = []

        def resolve() -> None:
            try:
                for _ in range(100):
                    instance = container.resolve(_StressService)
                    assert instance is not None
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=resolve) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0

    def test_many_registrations(self) -> None:
        container = DependencyContainer()
        for i in range(500):
            container.register_singleton(type(f"_S{i}", (object,), {}))
        assert container.registration_count == 500

    def test_metrics_concurrent_increment(self) -> None:
        import threading
        from src.core.runtime.metrics import MetricRegistry
        registry = MetricRegistry()
        errors: list[Exception] = []

        def worker() -> None:
            try:
                for _ in range(200):
                    c = registry.counter("concurrent")
                    c.increment()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(25)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
        assert registry.get_counter("concurrent").value == 5000
