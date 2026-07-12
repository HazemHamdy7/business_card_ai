import time
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any, TypeVar

from src.core.constants import TIMER_PRECISION

F = TypeVar("F", bound=Callable[..., Any])


class Timer:
    def __init__(self) -> None:
        self._start: float | None = None
        self._elapsed: float = 0.0

    def start(self) -> None:
        self._start = time.perf_counter()
        self._elapsed = 0.0

    def stop(self) -> float:
        if self._start is None:
            return 0.0
        self._elapsed = time.perf_counter() - self._start
        self._start = None
        return round(self._elapsed, TIMER_PRECISION)

    @property
    def elapsed(self) -> float:
        if self._start is not None:
            return round(time.perf_counter() - self._start, TIMER_PRECISION)
        return round(self._elapsed, TIMER_PRECISION)

    def reset(self) -> None:
        self._start = None
        self._elapsed = 0.0


@contextmanager
def timer_context(name: str = "timer"):
    timer = Timer()
    timer.start()
    try:
        yield timer
    finally:
        elapsed = timer.stop()


def timer_decorator(name: str | None = None):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            timer = Timer()
            timer.start()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = timer.stop()
                label = name or func.__name__

        return wrapper  # type: ignore[return-value]

    return decorator
