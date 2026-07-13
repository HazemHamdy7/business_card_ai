import time

from src.core.runtime.metrics import Counter, Gauge, Histogram, MetricRegistry, Timer


class TestCounter:
    def test_increment(self) -> None:
        c = Counter("test")
        c.increment()
        assert c.value == 1
        c.increment(5)
        assert c.value == 6

    def test_decrement(self) -> None:
        c = Counter("test")
        c.increment(10)
        c.decrement(3)
        assert c.value == 7

    def test_reset(self) -> None:
        c = Counter("test")
        c.increment(10)
        c.reset()
        assert c.value == 0

    def test_to_dict(self) -> None:
        c = Counter("test", "A test counter")
        d = c.to_dict()
        assert d["type"] == "counter"
        assert d["name"] == "test"
        assert d["value"] == 0


class TestGauge:
    def test_set(self) -> None:
        g = Gauge("test")
        g.set(42.5)
        assert g.value == 42.5

    def test_increment(self) -> None:
        g = Gauge("test")
        g.set(10.0)
        g.increment(5.0)
        assert g.value == 15.0

    def test_decrement(self) -> None:
        g = Gauge("test")
        g.set(10.0)
        g.decrement(3.0)
        assert g.value == 7.0

    def test_reset(self) -> None:
        g = Gauge("test")
        g.set(42.0)
        g.reset()
        assert g.value == 0.0

    def test_to_dict(self) -> None:
        g = Gauge("test", "A test gauge")
        g.set(42.5)
        d = g.to_dict()
        assert d["type"] == "gauge"
        assert d["value"] == 42.5


class TestHistogram:
    def test_observe(self) -> None:
        h = Histogram("test")
        h.observe(0.2)
        h.observe(0.8)
        h.observe(3.0)
        assert h.count == 3
        assert h.sum > 0
        assert h.avg > 0

    def test_reset(self) -> None:
        h = Histogram("test")
        h.observe(1.0)
        h.reset()
        assert h.count == 0
        assert h.sum == 0.0

    def test_to_dict(self) -> None:
        h = Histogram("test")
        h.observe(0.5)
        d = h.to_dict()
        assert d["type"] == "histogram"
        assert d["total"] == 1


class TestTimer:
    def test_record(self) -> None:
        t = Timer("test")
        t.record(1.5)
        assert t.histogram.count == 1

    def test_time_context(self) -> None:
        t = Timer("test")
        with t.time():
            pass
        assert t.histogram.count == 1

    def test_to_dict(self) -> None:
        t = Timer("test")
        t.record(1.0)
        d = t.to_dict()
        assert d["type"] == "timer"


class TestMetricRegistry:
    def setup_method(self) -> None:
        self.registry = MetricRegistry()

    def test_counter(self) -> None:
        c = self.registry.counter("requests")
        c.increment()
        assert c.value == 1

    def test_gauge(self) -> None:
        g = self.registry.gauge("temperature")
        g.set(36.5)
        assert g.value == 36.5

    def test_histogram(self) -> None:
        h = self.registry.histogram("latency")
        h.observe(0.5)
        assert h.count == 1

    def test_timer(self) -> None:
        t = self.registry.timer("processing")
        t.record(1.5)
        assert t.histogram.count == 1

    def test_get_metric(self) -> None:
        self.registry.counter("test")
        assert self.registry.get_counter("test") is not None
        assert self.registry.get_gauge("nonexistent") is None

    def test_reset_all(self) -> None:
        c = self.registry.counter("test")
        c.increment(10)
        self.registry.reset_all()
        assert c.value == 0

    def test_to_dict(self) -> None:
        self.registry.counter("requests")
        d = self.registry.to_dict()
        assert "counters" in d

    def test_to_json(self) -> None:
        self.registry.counter("requests")
        json_str = self.registry.to_json()
        assert '"requests"' in json_str
