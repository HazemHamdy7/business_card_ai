from src.core.environment import EnvironmentInfo, get_environment_info


class TestEnvironment:
    def test_environment_info_creation(self) -> None:
        info = EnvironmentInfo()
        assert info.python_version is not None
        assert info.operating_system is not None
        assert info.pytorch_version is not None
        assert isinstance(info.cuda_available, bool)
        assert info.cpu_count > 0
        assert isinstance(info.is_ci, bool)

    def test_environment_info_to_dict(self) -> None:
        info = EnvironmentInfo()
        d = info.to_dict()
        assert "python_version" in d
        assert "operating_system" in d
        assert "pytorch_version" in d
        assert "cuda_available" in d
        assert "cpu_count" in d
        assert "is_ci" in d

    def test_get_environment_info(self) -> None:
        info = get_environment_info()
        assert isinstance(info, dict)
        assert "python_version" in info
        assert "operating_system" in info
