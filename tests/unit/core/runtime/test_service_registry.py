import pytest

from src.core.exceptions import ServiceNotFoundError
from src.core.runtime.service_registry import ServiceRegistry


class _MockService:
    def __init__(self, name: str = "default") -> None:
        self.name = name


class TestServiceRegistry:
    def setup_method(self) -> None:
        self.registry = ServiceRegistry()

    def test_register_and_get(self) -> None:
        service = _MockService("test")
        self.registry.register("test", service)
        retrieved = self.registry.get("test")
        assert retrieved is service

    def test_register_duplicate_raises(self) -> None:
        self.registry.register("test", _MockService("a"))
        with pytest.raises(ServiceNotFoundError):
            self.registry.register("test", _MockService("b"))

    def test_register_override(self) -> None:
        service_a = _MockService("a")
        service_b = _MockService("b")
        self.registry.register("test", service_a)
        self.registry.register("test", service_b, override=True)
        retrieved = self.registry.get("test")
        assert retrieved is service_b

    def test_get_not_found(self) -> None:
        with pytest.raises(ServiceNotFoundError):
            self.registry.get("nonexistent")

    def test_get_or_none(self) -> None:
        assert self.registry.get_or_none("nonexistent") is None
        service = _MockService("test")
        self.registry.register("test", service)
        assert self.registry.get_or_none("test") is service

    def test_is_registered(self) -> None:
        assert not self.registry.is_registered("test")
        self.registry.register("test", _MockService("test"))
        assert self.registry.is_registered("test")

    def test_unregister(self) -> None:
        self.registry.register("test", _MockService("test"))
        self.registry.unregister("test")
        assert not self.registry.is_registered("test")

    def test_clear(self) -> None:
        self.registry.register("a", _MockService("a"))
        self.registry.register("b", _MockService("b"))
        self.registry.clear()
        assert self.registry.count == 0

    def test_count(self) -> None:
        assert self.registry.count == 0
        self.registry.register("a", _MockService("a"))
        assert self.registry.count == 1

    def test_list_services(self) -> None:
        self.registry.register("b", _MockService("b"))
        self.registry.register("a", _MockService("a"))
        services = self.registry.list_services()
        assert services == ["a", "b"]
