from src.core.device import get_device_info


class TestDeviceInfo:
    def test_get_device_info(self):
        info = get_device_info()
        assert info.device_type in ("cpu", "cuda", "mps")
        assert info.cpu_count >= 1
        assert "cuda_available" in info.to_dict()
        assert "device_type" in info.to_dict()
