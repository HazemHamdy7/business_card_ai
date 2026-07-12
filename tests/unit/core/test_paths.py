from pathlib import Path

from src.core.paths import Paths


class TestPaths:
    def test_root_is_path(self) -> None:
        assert isinstance(Paths.root(), Path)

    def test_root_contains_pyproject_toml(self) -> None:
        assert (Paths.root() / "pyproject.toml").exists()

    def test_config_dir(self) -> None:
        assert Paths.config_dir() == Paths.root() / "config"

    def test_dataset_dir(self) -> None:
        assert Paths.dataset_dir() == Paths.root() / "dataset"

    def test_models_dir(self) -> None:
        assert Paths.models_dir() == Paths.root() / "models"

    def test_logs_dir(self) -> None:
        assert Paths.logs_dir() == Paths.root() / "logs"

    def test_docs_dir(self) -> None:
        assert Paths.docs_dir() == Paths.root() / "docs"

    def test_config_file(self) -> None:
        assert Paths.config_file() == Paths.root() / "config" / "config.yaml"

    def test_env_file(self) -> None:
        assert Paths.env_file() == Paths.root() / ".env"

    def test_ensure_dirs_creates_directories(self, tmp_path: Path) -> None:
        original_root = Paths._root
        Paths._root = tmp_path
        try:
            Paths.ensure_dirs()
            assert (tmp_path / "config").exists()
            assert (tmp_path / "dataset").exists()
            assert (tmp_path / "models").exists()
            assert (tmp_path / "logs").exists()
            assert (tmp_path / "docs").exists()
        finally:
            Paths._root = original_root

    def test_root_is_absolute(self) -> None:
        assert Paths.root().is_absolute()
