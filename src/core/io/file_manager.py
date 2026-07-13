import shutil
from pathlib import Path
from typing import Any

from src.core.exceptions import FileError


class FileManager:
    @staticmethod
    def read_text(path: Path, encoding: str = "utf-8") -> str:
        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            raise FileError(f"Failed to read text from {path}: {e}") from e

    @staticmethod
    def write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)
        except Exception as e:
            raise FileError(f"Failed to write text to {path}: {e}") from e

    @staticmethod
    def read_bytes(path: Path) -> bytes:
        try:
            return path.read_bytes()
        except Exception as e:
            raise FileError(f"Failed to read bytes from {path}: {e}") from e

    @staticmethod
    def write_bytes(path: Path, data: bytes) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        except Exception as e:
            raise FileError(f"Failed to write bytes to {path}: {e}") from e

    @staticmethod
    def copy(source: Path, destination: Path) -> Path:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            return Path(shutil.copy2(str(source), str(destination)))
        except Exception as e:
            raise FileError(f"Failed to copy {source} to {destination}: {e}") from e

    @staticmethod
    def move(source: Path, destination: Path) -> Path:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            return Path(shutil.move(str(source), str(destination)))
        except Exception as e:
            raise FileError(f"Failed to move {source} to {destination}: {e}") from e

    @staticmethod
    def delete(path: Path) -> None:
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(str(path))
        except Exception as e:
            raise FileError(f"Failed to delete {path}: {e}") from e

    @staticmethod
    def exists(path: Path) -> bool:
        return path.exists()

    @staticmethod
    def size(path: Path) -> int:
        try:
            if path.is_file():
                return path.stat().st_size
            if path.is_dir():
                total = 0
                for item in path.rglob("*"):
                    if item.is_file():
                        total += item.stat().st_size
                return total
            return 0
        except Exception as e:
            raise FileError(f"Failed to get size of {path}: {e}") from e

    @staticmethod
    def extension(path: Path) -> str:
        return path.suffix.lower()

    @staticmethod
    def stem(path: Path) -> str:
        return path.stem

    @staticmethod
    def rename(source: Path, new_name: str) -> Path:
        try:
            destination = source.parent / new_name
            source.rename(destination)
            return destination
        except Exception as e:
            raise FileError(f"Failed to rename {source} to {new_name}: {e}") from e
