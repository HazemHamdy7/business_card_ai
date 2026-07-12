import time

from src.core.timer import Timer, timer_context, timer_decorator


class TestTimer:
    def test_timer_start_stop(self) -> None:
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        elapsed = timer.stop()
        assert elapsed > 0.0

    def test_timer_elapsed_during_run(self) -> None:
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        elapsed = timer.elapsed
        assert elapsed > 0.0
        timer.stop()

    def test_timer_reset(self) -> None:
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        timer.stop()
        assert timer.elapsed > 0.0
        timer.reset()
        assert timer.elapsed == 0.0

    def test_timer_stop_returns_elapsed(self) -> None:
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        elapsed = timer.stop()
        assert elapsed > 0.0

    def test_timer_stop_without_start(self) -> None:
        timer = Timer()
        assert timer.stop() == 0.0

    def test_timer_context_manager(self) -> None:
        from src.core.timer import timer_context

        with timer_context("test") as timer:
            time.sleep(0.01)
            assert timer.elapsed > 0.0

    def test_timer_decorator(self) -> None:
        from src.core.timer import timer_decorator

        @timer_decorator("test_func")
        def dummy() -> int:
            time.sleep(0.01)
            return 42

        result = dummy()
        assert result == 42
