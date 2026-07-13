import threading
from typing import Any

from src.core.exceptions import ServiceNotFoundError


class ServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[str, object] = {}
        self._lock = threading.Lock()

    def register(self, name: str, service: object, override: bool = False) -> None:
        with self._lock:
            if name in self._services and not override:
                raise ServiceNotFoundError(f"Service '{name}' already registered")
            self._services[name] = service

    def get(self, name: str) -> object:
        with self._lock:
            service = self._services.get(name)
            if service is None:
                raise ServiceNotFoundError(f"Service '{name}' not found")
            return service

    def get_or_none(self, name: str) -> object | None:
        with self._lock:
            return self._services.get(name)

    def is_registered(self, name: str) -> bool:
        with self._lock:
            return name in self._services

    def unregister(self, name: str) -> None:
        with self._lock:
            self._services.pop(name, None)

    def clear(self) -> None:
        with self._lock:
            self._services.clear()

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._services)

    def list_services(self) -> list[str]:
        with self._lock:
            return sorted(self._services.keys())
