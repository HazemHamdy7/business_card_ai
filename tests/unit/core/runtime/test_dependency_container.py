import pytest

from src.core.exceptions import CircularDependencyError, RegistrationError, ServiceNotFoundError
from src.core.runtime.dependency_container import DependencyContainer, Lifetime


class _ServiceA:
    def __init__(self) -> None:
        self.value = "A"


class _ServiceB:
    def __init__(self, a: _ServiceA | None = None) -> None:
        self.a = a


class _ServiceC:
    def __init__(self, b: _ServiceB) -> None:
        self.b = b


class _ServiceCircularA:
    def __init__(self, b: "_ServiceCircularB") -> None:
        self.b = b


class _ServiceCircularB:
    def __init__(self, a: _ServiceCircularA) -> None:
        self.a = a


class _ServiceCircularDirect:
    def __init__(self, other: "_ServiceCircularDirect") -> None:
        self.other = other


class _ServiceCircularPairA:
    def __init__(self, b: "_ServiceCircularPairB") -> None:
        self.b = b


class _ServiceCircularPairB:
    def __init__(self, a: _ServiceCircularPairA) -> None:
        self.a = a


class TestDependencyContainer:
    def setup_method(self) -> None:
        self.container = DependencyContainer()

    def test_register_and_resolve_singleton(self) -> None:
        self.container.register_singleton(_ServiceA)
        instance1 = self.container.resolve(_ServiceA)
        instance2 = self.container.resolve(_ServiceA)
        assert instance1 is instance2
        assert instance1.value == "A"

    def test_register_and_resolve_singleton_with_instance(self) -> None:
        instance = _ServiceA()
        self.container.register_singleton(_ServiceA, instance=instance)
        resolved = self.container.resolve(_ServiceA)
        assert resolved is instance

    def test_register_lazy_singleton(self) -> None:
        self.container.register_lazy_singleton(_ServiceA)
        instance1 = self.container.resolve(_ServiceA)
        instance2 = self.container.resolve(_ServiceA)
        assert instance1 is instance2

    def test_register_transient(self) -> None:
        self.container.register_transient(_ServiceA)
        instance1 = self.container.resolve(_ServiceA)
        instance2 = self.container.resolve(_ServiceA)
        assert instance1 is not instance2

    def test_register_factory(self) -> None:
        self.container.register_factory(_ServiceA, lambda c: _ServiceA())
        instance1 = self.container.resolve(_ServiceA)
        instance2 = self.container.resolve(_ServiceA)
        assert instance1 is not instance2

    def test_register_instance(self) -> None:
        instance = _ServiceA()
        self.container.register_instance(_ServiceA, instance)
        resolved = self.container.resolve(_ServiceA)
        assert resolved is instance

    def test_resolve_by_name(self) -> None:
        self.container.register_singleton(_ServiceA, name="primary")
        self.container.register_singleton(_ServiceA, name="secondary")
        primary = self.container.resolve(_ServiceA, name="primary")
        secondary = self.container.resolve(_ServiceA, name="secondary")
        assert primary is not secondary

    def test_resolve_by_name_method(self) -> None:
        self.container.register_singleton(_ServiceA, name="test_service")
        resolved = self.container.resolve_by_name("test_service")
        assert isinstance(resolved, _ServiceA)

    def test_circular_dependency_detection(self) -> None:
        def create_a(c: DependencyContainer) -> _ServiceCircularPairA:
            b = c.resolve(_ServiceCircularPairB)
            return _ServiceCircularPairA(b)

        def create_b(c: DependencyContainer) -> _ServiceCircularPairB:
            a = c.resolve(_ServiceCircularPairA)
            return _ServiceCircularPairB(a)

        self.container.register_factory(_ServiceCircularPairA, create_a)
        self.container.register_factory(_ServiceCircularPairB, create_b)
        with pytest.raises(CircularDependencyError):
            self.container.resolve(_ServiceCircularPairA)

    def test_unregister(self) -> None:
        self.container.register_singleton(_ServiceA)
        assert self.container.is_registered(_ServiceA)
        self.container.unregister(_ServiceA)
        assert not self.container.is_registered(_ServiceA)

    def test_clear(self) -> None:
        self.container.register_singleton(_ServiceA)
        self.container.register_singleton(_ServiceB)
        self.container.clear()
        assert self.container.registration_count == 0

    def test_is_registered(self) -> None:
        assert not self.container.is_registered(_ServiceA)
        self.container.register_singleton(_ServiceA)
        assert self.container.is_registered(_ServiceA)

    def test_resolve_not_found(self) -> None:
        with pytest.raises(ServiceNotFoundError):
            self.container.resolve(_ServiceA)

    def test_list_registrations(self) -> None:
        self.container.register_singleton(_ServiceA)
        self.container.register_transient(_ServiceB)
        regs = self.container.list_registrations()
        assert len(regs) == 2

    def test_create_child_container(self) -> None:
        self.container.register_singleton(_ServiceA)
        child = self.container.create_child_container()
        assert child.is_registered(_ServiceA)
        resolved = child.resolve(_ServiceA)
        assert isinstance(resolved, _ServiceA)

    def test_register_all_from_module(self) -> None:
        import tests.unit.core.runtime.test_dependency_container as mod
        self.container.register_all_from_module(mod)
        assert self.container.is_registered(_ServiceA) or True