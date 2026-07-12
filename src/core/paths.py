from pathlib import Path
from typing import ClassVar


class Paths:
    _root: ClassVar[Path | None] = None
    _MARKER_FILES: ClassVar[list[str]] = [".git", "pyproject.toml", "AGENTS.md"]

    @classmethod
    def _find_project_root(cls) -> Path:
        current = Path(__file__).resolve()
        for parent in current.parents:
            for marker in cls._MARKER_FILES:
                if (parent / marker).exists():
                    return parent
        return Path.cwd()

    @classmethod
    def root(cls) -> Path:
        if cls._root is None:
            cls._root = cls._find_project_root()
        return cls._root

    @classmethod
    def config_dir(cls) -> Path:
        return cls.root() / "config"

    @classmethod
    def dataset_dir(cls) -> Path:
        return cls.root() / "dataset"

    @classmethod
    def models_dir(cls) -> Path:
        return cls.root() / "models"

    @classmethod
    def logs_dir(cls) -> Path:
        return cls.root() / "logs"

    @classmethod
    def docs_dir(cls) -> Path:
        return cls.root() / "docs"

    @classmethod
    def config_file(cls) -> Path:
        return cls.config_dir() / "config.yaml"

    @classmethod
    def env_file(cls) -> Path:
        return cls.root() / ".env"

    @classmethod
    def ensure_dirs(cls) -> None:
        for directory in [cls.config_dir(), cls.dataset_dir(), cls.models_dir(), cls.logs_dir(), cls.docs_dir()]:
            directory.mkdir(parents=True, exist_ok=True)
