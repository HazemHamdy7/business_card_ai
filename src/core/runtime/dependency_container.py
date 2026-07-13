import threading
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, TypeVar

from src.core.exceptions import CircularDependencyError, RegistrationError, ServiceNotFoundError

T = TypeVar("T")


class Lifetime(Enum):
    SINGLETON = "singleton"
    LAZY_SINGLETON = "lazy_singleton"
    TRANSIENT = "transient"
    FACTORY = "factory"


class Registration(Generic[T]):
    def __init__(
        self,
        lifetime: Lifetime,
        factory: Callable[..., T] | None = None,
        instance: T | None = None,
        name: str | None = None,
    ) -> None:
        self.lifetime = lifetime
        self.factory = factory
        self.instance = instance
        self.name = name


class DependencyContainer:
    def __init__(self) -> None:
        self._registrations: dict[str, Registration] = {}
        self._instances: dict[str, object] = {}
        self._resolution_stack: list[str] = []
        self._lock = threading.Lock()

    def register_singleton(self, service_type: type, instance: object = None, name: str | None = None) -> None:
        key = self._key(service_type, name)
        if instance is not None:
            self._registrations[key] = Registration(Lifetime.SINGLETON, instance=instance, name=name)
            self._instances[key] = instance
        else:
            self._registrations[key] = Registration(Lifetime.SINGLETON, factory=self._auto_factory(service_type), name=name)

    def register_lazy_singleton(self, service_type: type, factory: Callable | None = None, name: str | None = None) -> None:
        key = self._key(service_type, name)
        self._registrations[key] = Registration(
            Lifetime.LAZY_SINGLETON,
            factory=factory or self._auto_factory(service_type),
            name=name,
        )

    def register_transient(self, service_type: type, factory: Callable | None = None, name: str | None = None) -> None:
        key = self._key(service_type, name)
        self._registrations[key] = Registration(
            Lifetime.TRANSIENT,
            factory=factory or self._auto_factory(service_type),
            name=name,
        )

    def register_factory(self, service_type: type, factory: Callable, name: str | None = None) -> None:
        key = self._key(service_type, name)
        self._registrations[key] = Registration(Lifetime.FACTORY, factory=factory, name=name)

    def register_instance(self, service_type: type, instance: object, name: str | None = None) -> None:
        key = self._key(service_type, name)
        self._registrations[key] = Registration(Lifetime.SINGLETON, instance=instance, name=name)
        self._instances[key] = instance

    def resolve(self, service_type: type[T], name: str | None = None) -> T:
        key = self._key(service_type, name)
        registration = self._registrations.get(key)
        if registration is None:
            type_name = getattr(service_type, "__name__", str(service_type))
            raise ServiceNotFoundError(f"No registration found for {type_name}" + (f" named '{name}'" if name else ""))

        if key in self._resolution_stack:
            raise CircularDependencyError(
                f"Circular dependency detected: {' -> '.join(self._resolution_stack + [key])}"
            )

        self._resolution_stack.append(key)

        try:
            if registration.lifetime == Lifetime.SINGLETON:
                if key not in self._instances:
                    if registration.instance is not None:
                        self._instances[key] = registration.instance
                    elif registration.factory is not None:
                        self._instances[key] = registration.factory(self)
                    else:
                        raise RegistrationError(f"No factory or instance for singleton {key}")
                return self._instances[key]

            if registration.lifetime == Lifetime.LAZY_SINGLETON:
                if key not in self._instances:
                    if registration.factory is not None:
                        self._instances[key] = registration.factory(self)
                    else:
                        raise RegistrationError(f"No factory for lazy singleton {key}")
                return self._instances[key]

            if registration.lifetime == Lifetime.TRANSIENT:
                if registration.factory is not None:
                    return registration.factory(self)
                raise RegistrationError(f"No factory for transient {key}")

            if registration.lifetime == Lifetime.FACTORY:
                if registration.factory is not None:
                    return registration.factory(self)
                raise RegistrationError(f"No factory for factory registration {key}")

            raise RegistrationError(f"Unknown lifetime: {registration.lifetime}")
        finally:
            self._resolution_stack.pop()

    def resolve_by_name(self, name: str) -> object:
        for key, reg in self._registrations.items():
            if reg.name == name:
                return self.resolve(self._type_from_key(key), name)
        raise ServiceNotFoundError(f"No service registered with name '{name}'")

    def is_registered(self, service_type: type, name: str | None = None) -> bool:
        key = self._key(service_type, name)
        return key in self._registrations

    def unregister(self, service_type: type, name: str | None = None) -> None:
        key = self._key(service_type, name)
        self._registrations.pop(key, None)
        self._instances.pop(key, None)

    def clear(self) -> None:
        self._registrations.clear()
        self._instances.clear()
        self._resolution_stack.clear()

    @property
    def registration_count(self) -> int:
        return len(self._registrations)

    @property
    def instance_count(self) -> int:
        return len(self._instances)

    def list_registrations(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for key, reg in self._registrations.items():
            result.append({
                "key": key,
                "lifetime": reg.lifetime.value,
                "name": reg.name,
                "has_factory": reg.factory is not None,
                "has_instance": reg.instance is not None,
                "is_resolved": key in self._instances,
            })
        return result

    @staticmethod
    def _key(service_type: type, name: str | None = None) -> str:
        import typing
        origin = getattr(service_type, "__origin__", None)
        if origin is not None:
            service_type = origin
        if hasattr(service_type, "__module__") and hasattr(service_type, "__qualname__"):
            return f"{service_type.__module__}.{service_type.__qualname__}" + (f":{name}" if name else "")
        return str(service_type) + (f":{name}" if name else "")

    @staticmethod
    def _type_from_key(key: str) -> type:
        module_part, _, qualname = key.partition(":")
        parts = module_part.rsplit(".", 1)
        if len(parts) == 2:
            import importlib
            module = importlib.import_module(parts[0])
            return getattr(module, parts[1])
        raise ServiceNotFoundError(f"Cannot resolve type from key: {key}")

    @staticmethod
    def _auto_factory(service_type: type) -> Callable:
        def factory(container: DependencyContainer) -> object:
            import inspect
            import typing
            init = service_type.__init__
            sig = inspect.signature(init)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                annotation = param.annotation
                if annotation is not inspect.Parameter.empty:
                    if isinstance(annotation, str):
                        if param.default is not inspect.Parameter.empty:
                            params[param_name] = param.default
                        continue
                    origin = getattr(annotation, "__origin__", None)
                    if origin is typing.Union:
                        args = annotation.__args__
                        for arg in args:
                            if arg is not type(None):
                                try:
                                    params[param_name] = container.resolve(arg)
                                    break
                                except ServiceNotFoundError:
                                    continue
                        if param_name not in params and param.default is not inspect.Parameter.empty:
                            params[param_name] = param.default
                        continue
                    try:
                        params[param_name] = container.resolve(annotation)
                    except ServiceNotFoundError:
                        if param.default is not inspect.Parameter.empty:
                            params[param_name] = param.default
                        else:
                            raise
                elif param.default is not inspect.Parameter.empty:
                    params[param_name] = param.default
            return service_type(**params)
        return factory

    def register_all_from_module(self, module: object, prefix: str | None = None) -> None:
        import inspect
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == getattr(module, "__name__", ""):
                reg_name = f"{prefix}:{name}" if prefix else name
                self.register_lazy_singleton(obj, name=reg_name)

    def create_child_container(self) -> "DependencyContainer":
        child = DependencyContainer()
        child._registrations = dict(self._registrations)
        child._instances = dict(self._instances)
        return child