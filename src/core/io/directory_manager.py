import shutil
from pathlib import Path

from src.core.exceptions import FileError


class DirectoryManager:
    @staticmethod
    def create(path: Path, parents: bool = True, exist_ok: bool = True) -> Path:
        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
            return path
        except Exception as e:
            raise FileError(f"Failed to create directory {path}: {e}") from e

    @staticmethod
    def delete(path: Path, missing_ok: bool = True) -> None:
        if not path.exists() and missing_ok:
            return
        try:
            import shutil
            shutil.rmtree(str(path))
        except Exception as e:
            raise FileError(f"Failed to delete directory {path}: {e}") from e

    @staticmethod
    def clean(path: Path) -> None:
        if not path.exists():
            return
        try:
            for item in path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(str(item))
        except Exception as e:
            raise FileError(f"Failed to clean directory {path}: {e}") from e

    @staticmethod
    def exists(path: Path) -> bool:
        return path.is_dir()

    @staticmethod
    def tree(path: Path, prefix: str = "", max_depth: int = 3) -> list[str]:
        if not path.is_dir():
            return [str(path)]
        lines: list[str] = []
        items = sorted(path.iterdir())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{item.name}")
            if item.is_dir():
                extension = "    " if is_last else "│   "
                if max_depth > 1:
                    lines.extend(DirectoryManager.tree(item, prefix + extension, max_depth - 1))
        return lines

    @staticmethod
    def create_temp(prefix: str = "bca_") -> Path:
        import tempfile
        return Path(tempfile.mkdtemp(prefix=prefix))
