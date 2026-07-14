from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import get_core_logger

from .dataset_loader import DatasetInfo
from .yolo_config import YOLOModelConfig


@dataclass
class YOLOBatchStats:
    batch_size: int = 0
    num_batches: int = 0
    total_samples: int = 0
    image_size: int = 640
    mosaic_active: bool = False
    mixup_active: bool = False
    rect_training: bool = False
    cache_images: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class YOLODataPipeline:
    def __init__(self, model_config: YOLOModelConfig):
        self.model_config = model_config
        self.logger = get_core_logger()
        self._train_dataset: Any = None
        self._val_dataset: Any = None
        self._test_dataset: Any = None
        self._train_loader: Any = None
        self._val_loader: Any = None
        self._test_loader: Any = None

    def build_pipeline(
        self,
        dataset_info: DatasetInfo,
        dataset_root: str,
        batch_size: int,
        workers: int = 4,
        pin_memory: bool = True,
    ) -> YOLOBatchStats:
        self.logger.info(
            "Building YOLO data pipeline",
            extra={
                "dataset_root": dataset_root,
                "batch_size": batch_size,
                "workers": workers,
                "input_size": self.model_config.input_size,
            },
        )

        stats = YOLOBatchStats(
            batch_size=batch_size,
            image_size=self.model_config.input_size,
            mosaic_active=self.model_config.augmentation.mosaic > 0,
            mixup_active=self.model_config.augmentation.mixup > 0,
            rect_training=self.model_config.rect_training,
            cache_images=self.model_config.cache_images,
        )

        total_samples = dataset_info.total_images
        stats.total_samples = total_samples
        stats.num_batches = max(1, total_samples // batch_size) if total_samples > 0 else 0

        self._build_datasets(dataset_info, dataset_root)
        self._build_loaders(batch_size, workers, pin_memory)

        self.logger.info(
            "YOLO data pipeline built",
            extra={
                "total_samples": stats.total_samples,
                "num_batches": stats.num_batches,
                "batch_size": stats.batch_size,
            },
        )
        return stats

    def _build_datasets(
        self, dataset_info: DatasetInfo, dataset_root: str
    ) -> None:
        self._train_dataset = None
        self._val_dataset = None
        self._test_dataset = None

        if dataset_info.train_images > 0:
            train_dir = self._resolve_data_dir(dataset_root, "train")
            self._train_dataset = {"path": train_dir, "samples": dataset_info.train_images}

        if dataset_info.val_images > 0:
            val_dir = self._resolve_data_dir(dataset_root, "val")
            self._val_dataset = {"path": val_dir, "samples": dataset_info.val_images}

        if dataset_info.test_images > 0:
            test_dir = self._resolve_data_dir(dataset_root, "test")
            self._test_dataset = {"path": test_dir, "samples": dataset_info.test_images}

    def _build_loaders(
        self, batch_size: int, workers: int, pin_memory: bool
    ) -> None:
        self._train_loader = None
        self._val_loader = None
        self._test_loader = None

        if self._train_dataset:
            self._train_loader = {
                "batch_size": batch_size,
                "shuffle": True,
                "num_workers": workers,
                "pin_memory": pin_memory,
                "drop_last": True,
            }

        if self._val_dataset:
            self._val_loader = {
                "batch_size": batch_size,
                "shuffle": False,
                "num_workers": workers,
                "pin_memory": pin_memory,
                "drop_last": False,
            }

        if self._test_dataset:
            self._test_loader = {
                "batch_size": batch_size,
                "shuffle": False,
                "num_workers": workers,
                "pin_memory": pin_memory,
                "drop_last": False,
            }

    def _resolve_data_dir(self, root: str, split: str) -> str:
        candidate = os.path.join(root, split, "images")
        if os.path.isdir(candidate):
            return candidate
        return os.path.join(root, split)

    @property
    def train_loader(self) -> Any:
        return self._train_loader

    @property
    def val_loader(self) -> Any:
        return self._val_loader

    @property
    def test_loader(self) -> Any:
        return self._test_loader

    def get_dataset_sizes(self) -> Dict[str, int]:
        sizes: Dict[str, int] = {}
        if self._train_dataset:
            sizes["train"] = self._train_dataset["samples"]
        if self._val_dataset:
            sizes["val"] = self._val_dataset["samples"]
        if self._test_dataset:
            sizes["test"] = self._test_dataset["samples"]
        return sizes

    def get_augmentation_info(self) -> Dict[str, Any]:
        aug = self.model_config.augmentation
        return {
            "mosaic": aug.mosaic,
            "mixup": aug.mixup,
            "copy_paste": aug.copy_paste,
            "degrees": aug.degrees,
            "translate": aug.translate,
            "scale": aug.scale,
            "shear": aug.shear,
            "flipud": aug.flipud,
            "fliplr": aug.fliplr,
            "hsv_h": aug.hsv_h,
            "hsv_s": aug.hsv_s,
            "hsv_v": aug.hsv_v,
            "auto_augment": aug.auto_augment,
            "erasing": aug.erasing,
            "crop_fraction": aug.crop_fraction,
        }
