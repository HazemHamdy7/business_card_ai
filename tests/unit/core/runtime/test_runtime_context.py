from src.core.runtime.runtime_context import RuntimeContext


class TestRuntimeContext:
    def test_initialization(self) -> None:
        ctx = RuntimeContext()
        assert ctx.version == "0.1.0"
        assert "Business Card AI" in ctx.full_version
        assert not ctx.is_initialized

    def test_initialize(self) -> None:
        ctx = RuntimeContext()
        ctx.initialize()
        assert ctx.is_initialized
        assert ctx.device is not None
        assert ctx.environment is not None
        assert ctx.cache is not None

    def test_config(self) -> None:
        ctx = RuntimeContext()
        assert ctx.config is not None

    def test_logger(self) -> None:
        ctx = RuntimeContext()
        assert ctx.logger is not None

    def test_device(self) -> None:
        ctx = RuntimeContext()
        device = ctx.device
        assert device.device_type in ("cpu", "cuda")

    def test_environment(self) -> None:
        ctx = RuntimeContext()
        env = ctx.environment
        assert env.python_version is not None

    def test_paths(self) -> None:
        ctx = RuntimeContext()
        assert ctx.paths is not None

    def test_to_dict(self) -> None:
        ctx = RuntimeContext()
        d = ctx.to_dict()
        assert "version" in d
        assert "device" in d
        assert "environment" in d
