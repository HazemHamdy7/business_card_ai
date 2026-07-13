import json
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class Counter:
    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self._description = description
        self._value: int = 0
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> None:
        with self._lock:
            self._value += amount

    def decrement(self, amount: int = 1) -> None:
        with self._lock:
            self._value -= amount

    def reset(self) -> None:
        with self._lock:
            self._value = 0

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

    @property
    def name(self) -> str:
        return self._name

    def to_dict(self) -> dict[str, Any]:
        return {"type": "counter", "name": self._name, "description": self._description, "value": self.value}


class Gauge:
    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self._description = description
        self._value: float = 0.0
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def increment(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def decrement(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    def reset(self) -> None:
        with self._lock:
            self._value = 0.0

    @property
    def value(self) -> float:
        with self._lock:
            return self._value

    @property
    def name(self) -> str:
        return self._name

    def to_dict(self) -> dict[str, Any]:
        return {"type": "gauge", "name": self._name, "description": self._description, "value": self._value}


class Histogram:
    def __init__(self, name: str, description: str = "", buckets: list[float] | None = None) -> None:
        self._name = name
        self._description = description
        self._buckets = sorted(buckets) if buckets else [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        self._counts: list[int] = [0] * (len(self._buckets) + 1)
        self._total: int = 0
        self._sum: float = 0.0
        self._lock = threading.RLock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._total += 1
            self._sum += value
            for i, bucket in enumerate(self._buckets):
                if value <= bucket:
                    self._counts[i] += 1
                    return
            self._counts[-1] += 1

    def reset(self) -> None:
        with self._lock:
            self._counts = [0] * (len(self._buckets) + 1)
            self._total = 0
            self._sum = 0.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def count(self) -> int:
        with self._lock:
            return self._total

    @property
    def sum(self) -> float:
        with self._lock:
            return self._sum

    @property
    def avg(self) -> float:
        with self._lock:
            return round(self._sum / self._total, 4) if self._total > 0 else 0.0

    @property
    def min(self) -> float:
        return 0.0

    @property
    def max(self) -> float:
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                "type": "histogram",
                "name": self._name,
                "description": self._description,
                "buckets": self._buckets,
                "counts": list(self._counts),
                "total": self._total,
                "sum": self._sum,
                "avg": self.avg,
            }


class Timer:
    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self._description = description
        self._histogram = Histogram(name, description)
        self._lock = threading.Lock()

    def record(self, seconds: float) -> None:
        self._histogram.observe(seconds)

    @contextmanager
    def time(self) -> Any:
        import time
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.record(elapsed)

    @property
    def name(self) -> str:
        return self._name

    @property
    def histogram(self) -> Histogram:
        return self._histogram

    def to_dict(self) -> dict[str, Any]:
        return {"type": "timer", "name": self._name, "description": self._description, "histogram": self._histogram.to_dict()}


class MetricRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._timers: dict[str, Timer] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, description: str = "") -> Counter:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name, description)
            return self._counters[name]

    def gauge(self, name: str, description: str = "") -> Gauge:
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name, description)
            return self._gauges[name]

    def histogram(self, name: str, description: str = "", buckets: list[float] | None = None) -> Histogram:
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, description, buckets)
            return self._histograms[name]

    def timer(self, name: str, description: str = "") -> Timer:
        with self._lock:
            if name not in self._timers:
                self._timers[name] = Timer(name, description)
            return self._timers[name]

    def get_counter(self, name: str) -> Counter | None:
        with self._lock:
            return self._counters.get(name)

    def get_gauge(self, name: str) -> Gauge | None:
        with self._lock:
            return self._gauges.get(name)

    def get_histogram(self, name: str) -> Histogram | None:
        with self._lock:
            return self._histograms.get(name)

    def get_timer(self, name: str) -> Timer | None:
        with self._lock:
            return self._timers.get(name)

    def reset_all(self) -> None:
        with self._lock:
            for c in self._counters.values():
                c.reset()
            for g in self._gauges.values():
                g.reset()
            for h in self._histograms.values():
                h.reset()
            for t in self._timers.values():
                t.histogram.reset()

    def to_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": {n: c.to_dict() for n, c in self._counters.items()},
                "gauges": {n: g.to_dict() for n, g in self._gauges.items()},
                "histograms": {n: h.to_dict() for n, h in self._histograms.items()},
                "timers": {n: t.to_dict() for n, t in self._timers.items()},
            }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
