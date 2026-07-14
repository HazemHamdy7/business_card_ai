import pytest
from src.api.config import APIConfig
from src.api.health import get_health_info, get_system_info


class TestHealth:
    def test_get_health_info(self):
        config = APIConfig()
        info = get_health_info(config)
        assert info["status"] == "healthy"
        assert "version" in info
        assert "python_version" in info
        assert "gpu_available" in info
        assert "cuda_available" in info
        assert "uptime_seconds" in info
        assert "environment" in info

    def test_get_system_info(self):
        info = get_system_info()
        assert "python_version" in info
        assert "platform" in info
        assert "cpu_count" in info
        assert info["cpu_count"] >= 1

    def test_health_info_memory_optional(self):
        config = APIConfig()
        info = get_health_info(config)
        assert "memory_usage" in info

    def test_health_info_disk_optional(self):
        config = APIConfig()
        info = get_health_info(config)
        assert "disk_usage" in info
