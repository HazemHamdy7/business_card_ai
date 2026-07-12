from src.core.device import DeviceInfo, get_device


class TestDevice:
    def test_device_info_creation(self) -> None:
        info = DeviceInfo()
        assert info.device_type in ("cpu", "cuda")
        assert info.pytorch_version is not None
        assert info.python_version is not None
        assert info.operating_system is not None

    def test_device_info_is_cpu_or_cuda(self) -> None:
        info = DeviceInfo()
        assert info.is_cpu() or info.is_cuda()

    def test_device_info_to_dict(self) -> None:
        info = DeviceInfo()
        d = info.to_dict()
        assert "device_type" in d
        assert "gpu_name" in d
        assert "pytorch_version" in d
        assert "python_version" in d
        assert "operating_system" in d

    def test_get_device(self) -> None:
        info = get_device()
        assert isinstance(info, DeviceInfo)
