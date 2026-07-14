import pytest

from src.training.callbacks import (
    Callback,
    CallbackHandler,
    CallbackEvent,
    EarlyStoppingCallback,
    LoggingCallback,
)


class TestCallbackHandler:
    @pytest.fixture
    def handler(self):
        return CallbackHandler()

    def test_add_and_invoke(self, handler):
        events = []

        class TestCallback(Callback):
            def on_training_start(self, context):
                events.append("start")

            def on_epoch_end(self, context):
                events.append("epoch_end")

        cb = TestCallback()
        handler.add(cb)
        handler.invoke(CallbackEvent.TRAINING_START, {})
        handler.invoke(CallbackEvent.EPOCH_END, {})
        assert events == ["start", "epoch_end"]

    def test_add_function(self, handler):
        events = []

        def on_event(event, context):
            events.append(event)

        handler.add_function(CallbackEvent.TRAINING_START, on_event)
        handler.invoke(CallbackEvent.TRAINING_START, {})
        assert events == [CallbackEvent.TRAINING_START]

    def test_remove(self, handler):
        cb = Callback()
        handler.add(cb)
        handler.remove(cb)
        assert len(handler.get_callbacks()) == 0

    def test_clear(self, handler):
        handler.add(Callback())
        handler.add_function(CallbackEvent.TRAINING_START, lambda e, c: None)
        handler.clear()
        assert len(handler.get_callbacks()) == 0


class TestEarlyStoppingCallback:
    def test_no_stop_on_improvement(self):
        es = EarlyStoppingCallback(patience=3, delta=0.01)
        ctx = {}
        for loss in [0.5, 0.4, 0.3]:
            ctx["loss"] = loss
            ctx["epoch"] = 1
            es.on_epoch_end(ctx)
        assert "early_stop" not in ctx

    def test_stop_on_no_improvement(self):
        es = EarlyStoppingCallback(patience=2, delta=0.01)
        ctx = {}
        for loss in [0.5, 0.5, 0.5]:
            ctx["loss"] = loss
            ctx["epoch"] = 1
            es.on_epoch_end(ctx)
        assert ctx.get("early_stop") is True

    def test_reset(self):
        es = EarlyStoppingCallback(patience=2, delta=0.01)
        ctx = {}
        for _ in range(3):
            ctx["loss"] = 0.5
            es.on_epoch_end(ctx)
        assert ctx.get("early_stop") is True
        es.reset()
        ctx2 = {}
        for _ in range(3):
            ctx2["loss"] = 0.5
            es.on_epoch_end(ctx2)
        assert ctx2.get("early_stop") is True


class TestLoggingCallback:
    def test_epoch_end(self):
        captured = []

        class FakeLogger:
            def info(self, msg):
                captured.append(msg)

        cb = LoggingCallback(logger=FakeLogger())
        cb.on_epoch_end({
            "epoch": 5,
            "loss": 0.25,
            "learning_rate": 0.001,
            "epoch_time": 10.5,
        })
        assert len(captured) == 1
        assert "Epoch 5" in captured[0]
