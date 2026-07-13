from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from src.core.exceptions import FileError


class ImageIO:
    SUPPORTED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

    @staticmethod
    def read(path: Path) -> NDArray[Any]:
        if not path.exists():
            raise FileError(f"Image file not found: {path}")
        if path.suffix.lower() not in ImageIO.SUPPORTED_EXTENSIONS:
            raise FileError(f"Unsupported image format: {path.suffix}")
        image = cv2.imread(str(path))
        if image is None:
            raise FileError(f"Failed to read image: {path}")
        return image

    @staticmethod
    def write(path: Path, image: NDArray[Any]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(path), image)
            if not success:
                raise FileError(f"Failed to write image to {path}")
        except Exception as e:
            raise FileError(f"Failed to write image to {path}: {e}") from e

    @staticmethod
    def resize(image: NDArray[Any], width: int, height: int, interpolation: int = cv2.INTER_LINEAR) -> NDArray[Any]:
        return cv2.resize(image, (width, height), interpolation=interpolation)

    @staticmethod
    def to_rgb(image: NDArray[Any]) -> NDArray[Any]:
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    @staticmethod
    def to_bgr(image: NDArray[Any]) -> NDArray[Any]:
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    @staticmethod
    def metadata(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileError(f"Image file not found: {path}")
        image = ImageIO.read(path)
        return {
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "width": image.shape[1],
            "height": image.shape[0],
            "channels": image.shape[2] if len(image.shape) == 3 else 1,
            "dtype": str(image.dtype),
            "extension": path.suffix.lower(),
        }

    @staticmethod
    def validate(path: Path) -> bool:
        if not path.exists():
            return False
        if path.suffix.lower() not in ImageIO.SUPPORTED_EXTENSIONS:
            return False
        try:
            image = cv2.imread(str(path))
            return image is not None
        except Exception:
            return False
