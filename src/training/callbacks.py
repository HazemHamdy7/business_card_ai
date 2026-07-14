from __future__ import annotations

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional


class CallbackEvent(Enum):
    TRAINING_START = auto()
    TRAINING_END = auto()
    EPOCH_START = auto()
    EPOCH_END = auto()
    BATCH_START = auto()
    BATCH_END = auto()
    CHECKPOINT_SAVED = auto()
    EARLY_STOP = auto()
    EXCEPTION = auto()


CallbackFn = Callable[[CallbackEvent, Dict[str, Any]], None]


class Callback:
    def on_training_start(self, context: Dict[str, Any]) -> None:
        pass

    def on_training_end(self, context: Dict[str, Any]) -> None:
        pass

    def on_epoch_start(self, context: Dict[str, Any]) -> None:
        pass

    def on_epoch_end(self, context: Dict[str, Any]) -> None:
        pass

    def on_batch_start(self, context: Dict[str, Any]) -> None:
        pass

    def on_batch_end(self, context: Dict[str, Any]) -> None:
        pass

    def on_checkpoint_saved(self, context: Dict[str, Any]) -> None:
        pass

    def on_early_stop(self, context: Dict[str, Any]) -> None:
        pass

    def on_exception(self, context: Dict[str, Any]) -> None:
        pass


class CallbackHandler:
    def __init__(self):
        self._callbacks: List[Callback] = []
        self._functions: Dict[CallbackEvent, List[CallbackFn]] = {
            event: [] for event in CallbackEvent
        }

    def add(self, callback: Callback) -> None:
        self._callbacks.append(callback)

    def add_function(
        self, event: CallbackEvent, fn: CallbackFn
    ) -> None:
        self._functions[event].append(fn)

    def remove(self, callback: Callback) -> None:
        self._callbacks.remove(callback)

    def clear(self) -> None:
        self._callbacks.clear()
        for event in CallbackEvent:
            self._functions[event].clear()

    def invoke(self, event: CallbackEvent, context: Dict[str, Any]) -> None:
        event_map = {
            CallbackEvent.TRAINING_START: "on_training_start",
            CallbackEvent.TRAINING_END: "on_training_end",
            CallbackEvent.EPOCH_START: "on_epoch_start",
            CallbackEvent.EPOCH_END: "on_epoch_end",
            CallbackEvent.BATCH_START: "on_batch_start",
            CallbackEvent.BATCH_END: "on_batch_end",
            CallbackEvent.CHECKPOINT_SAVED: "on_checkpoint_saved",
            CallbackEvent.EARLY_STOP: "on_early_stop",
            CallbackEvent.EXCEPTION: "on_exception",
        }

        method_name = event_map.get(event)
        if method_name:
            for cb in self._callbacks:
                method = getattr(cb, method_name, None)
                if method:
                    try:
                        method(context)
                    except Exception:
                        pass

        for fn in self._functions[event]:
            try:
                fn(event, context)
            except Exception:
                pass

    def get_callbacks(self) -> List[Callback]:
        return list(self._callbacks)


class EarlyStoppingCallback(Callback):
    def __init__(self, patience: int = 10, delta: float = 0.001):
        self.patience = patience
        self.delta = delta
        self._counter = 0
        self._best_loss = float("inf")
        self._stopped_epoch = 0

    def on_epoch_end(self, context: Dict[str, Any]) -> None:
        loss = context.get("loss", float("inf"))
        epoch = context.get("epoch", 0)

        if loss < self._best_loss - self.delta:
            self._best_loss = loss
            self._counter = 0
        else:
            self._counter += 1

        if self._counter >= self.patience:
            context["early_stop"] = True
            context["early_stop_epoch"] = epoch
            self._stopped_epoch = epoch

    def reset(self) -> None:
        self._counter = 0
        self._best_loss = float("inf")
        self._stopped_epoch = 0


class LoggingCallback(Callback):
    def __init__(self, logger=None):
        self._logger = logger

    def on_epoch_end(self, context: Dict[str, Any]) -> None:
        epoch = context.get("epoch", 0)
        loss = context.get("loss", 0.0)
        lr = context.get("learning_rate", 0.0)
        epoch_time = context.get("epoch_time", 0.0)
        message = (
            f"Epoch {epoch}: loss={loss:.6f}, lr={lr:.8f}, "
            f"time={epoch_time:.2f}s"
        )
        if self._logger:
            self._logger.info(message)
