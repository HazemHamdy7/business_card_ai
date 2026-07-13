from src.core.runtime.dependency_container import DependencyContainer
from src.core.runtime.health_check import HealthCheck
from src.core.runtime.metrics import MetricRegistry
from src.core.runtime.performance_monitor import PerformanceMonitor
from src.core.runtime.runtime_context import RuntimeContext
from src.core.runtime.service_registry import ServiceRegistry


class _DatabaseService:
    def __init__(self) -> None:
        self.connected = False

    def connect(self) -> None:
        self.connected = True


class _UserService:
    def __init__(self, db: _DatabaseService) -> None:
        self.db = db


class TestRuntimeIntegration:
    def test_container_with_auto_wiring(self) -> None:
        from src.core.runtime.dependency_container import DependencyContainer
        container = DependencyContainer()
        container.register_singleton(_DatabaseService)
        container.register_lazy_singleton(_UserService)
        user = container.resolve(_UserService)
        assert isinstance(user, _UserService)
        assert isinstance(user.db, _DatabaseService)

    def test_runtime_context_with_container(self) -> None:
        from src.core.runtime.dependency_container import DependencyContainer
        from src.core.runtime.runtime_context import RuntimeContext
        container = DependencyContainer()
        container.register_singleton(RuntimeContext)
        ctx = container.resolve(RuntimeContext)
        assert isinstance(ctx, RuntimeContext)

    def test_metrics_with_performance_monitor(self) -> None:
        from src.core.runtime.metrics import MetricRegistry
        from src.core.runtime.performance_monitor import PerformanceMonitor
        registry = MetricRegistry()
        monitor = PerformanceMonitor()
        timer = registry.timer("execution")
        with timer.time():
            monitor.record_execution(0.5)
        assert timer.histogram.count == 1
        assert monitor.avg_execution_time == 0.5

    def test_health_check_with_runtime_context(self) -> None:
        from src.core.runtime.health_check import HealthCheck
        from src.core.runtime.runtime_context import RuntimeContext
        ctx = RuntimeContext()
        health = HealthCheck(ctx.config)
        results = health.run_all()
        assert len(results) == 7
