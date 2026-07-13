import shutil
import tempfile
from pathlib import Path
from typing import Generator


class TempManager:
    def __init__(self, prefix: str = "bca_") -> None:
        self._prefix = prefix
        self._temp_dirs: list[Path] = []

    def create_dir(self, suffix: str | None = None) -> Path:
        prefix = self._prefix
        if suffix:
            prefix = f"{self._prefix}{suffix}_"
        path = Path(tempfile.mkdtemp(prefix=prefix))
        self._temp_dirs.append(path)
        return path

    def create_file(self, suffix: str = ".tmp") -> Path:
        import tempfile
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=self._prefix)
        import os
        os.close(fd)
        return Path(path)

    def cleanup(self) -> None:
        import shutil
        for path in self._temp_dirs:
            if path.exists():
                shutil.rmtree(str(path), ignore_errors=True)
        self._temp_dirs.clear()

    def __enter__(self) -> "TempManager":
        return self

    def __exit__(self, *args: object) -> None:
        self.cleanup()
