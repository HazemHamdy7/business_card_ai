import pytest

from src.training.device_manager import DeviceManager, DeviceCapability


class TestDeviceManager:
    def test_cpu_device(self):
        dm = DeviceManager(device="cpu")
        assert dm.device == "cpu"
        cap = dm.capability
        assert not cap.cuda_available
        assert cap.cpu_count >= 1

    def test_auto_device(self):
        dm = DeviceManager(device="auto")
        assert dm.device in ("cpu", "cuda", "mps")

    def test_capability_properties(self):
        dm = DeviceManager(device="cpu")
        cap = dm.capability
        assert isinstance(cap, DeviceCapability)
        assert cap.max_batch_size >= 4
        assert cap.cpu_count >= 1

    def test_summary(self):
        dm = DeviceManager(device="cpu")
        summary = dm.summary()
        assert "Device: cpu" in summary
        assert "CPU Cores" in summary

    def test_get_device_info(self):
        dm = DeviceManager(device="cpu")
        info = dm.get_device_info()
        assert info.device_type in ("cpu", "cuda", "mps")

    def test_to_torch_device_cpu(self):
        dm = DeviceManager(device="cpu")
        td = dm.to_torch_device()
        assert td is not None
        assert str(td) == "cpu"
