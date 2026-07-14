from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.constants import SUPPORTED_IMG_FORMATS, YOLO_LABEL_EXT


@dataclass
class DatasetInfo:
    format: str = "yolo"
    num_classes: int = 0
    class_names: Dict[int, str] = field(default_factory=dict)
    train_images: int = 0
    train_labels: int = 0
    val_images: int = 0
    val_labels: int = 0
    test_images: int = 0
    test_labels: int = 0
    total_images: int = 0
    total_labels: int = 0
    image_size: int = 640
    has_valid_labels: bool = False
    missing_labels: List[str] = field(default_factory=list)
    invalid_labels: List[str] = field(default_factory=list)
    corrupted_images: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format,
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "train_images": self.train_images,
            "train_labels": self.train_labels,
            "val_images": self.val_images,
            "val_labels": self.val_labels,
            "test_images": self.test_images,
            "test_labels": self.test_labels,
            "total_images": self.total_images,
            "total_labels": self.total_labels,
            "image_size": self.image_size,
            "has_valid_labels": self.has_valid_labels,
        }


class DatasetLoader:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}

    def load(
        self,
        dataset_root: str,
        format: str = "yolo",
        train_image_dir: Optional[str] = None,
        train_label_dir: Optional[str] = None,
        val_image_dir: Optional[str] = None,
        val_label_dir: Optional[str] = None,
        test_image_dir: Optional[str] = None,
        test_label_dir: Optional[str] = None,
    ) -> DatasetInfo:
        if format == "yolo":
            return self._load_yolo(
                dataset_root, train_image_dir, train_label_dir,
                val_image_dir, val_label_dir, test_image_dir, test_label_dir,
            )
        elif format == "coco":
            return self._load_coco(dataset_root)
        else:
            return self._load_custom(
                dataset_root, train_image_dir, train_label_dir,
                val_image_dir, val_label_dir, test_image_dir, test_label_dir,
            )

    def _load_yolo(
        self,
        root: str,
        train_img: Optional[str],
        train_lbl: Optional[str],
        val_img: Optional[str],
        val_lbl: Optional[str],
        test_img: Optional[str],
        test_lbl: Optional[str],
    ) -> DatasetInfo:
        info = DatasetInfo(format="yolo")

        splits = [
            ("train", train_img, train_lbl),
            ("val", val_img, val_lbl),
            ("test", test_img, test_lbl),
        ]

        for split_name, img_dir, lbl_dir in splits:
            resolved_img = self._resolve_path(root, img_dir, split_name, "images")
            resolved_lbl = self._resolve_path(root, lbl_dir, split_name, "labels")

            images = self._count_images(resolved_img)
            labels = self._count_labels(resolved_lbl)

            setattr(info, f"{split_name}_images", images)
            setattr(info, f"{split_name}_labels", labels)
            info.total_images += images
            info.total_labels += labels

            self._validate_labels(resolved_lbl, info)

        info.has_valid_labels = (
            len(info.missing_labels) == 0
            and len(info.invalid_labels) == 0
        )

        return info

    def _load_coco(self, root: str) -> DatasetInfo:
        info = DatasetInfo(format="coco")
        json_path = os.path.join(root, "coco.json")
        if os.path.isfile(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                categories = data.get("categories", [])
                info.num_classes = len(categories)
                info.class_names = {
                    cat["id"]: cat["name"] for cat in categories
                }
                images = data.get("images", [])
                annotations = data.get("annotations", [])
                info.train_images = len(images)
                info.total_images = len(images)
                info.total_labels = len(annotations)
                info.has_valid_labels = True
            except Exception:
                pass
        return info

    def _load_custom(
        self,
        root: str,
        train_img: Optional[str],
        train_lbl: Optional[str],
        val_img: Optional[str],
        val_lbl: Optional[str],
        test_img: Optional[str],
        test_lbl: Optional[str],
    ) -> DatasetInfo:
        return self._load_yolo(
            root, train_img, train_lbl,
            val_img, val_lbl, test_img, test_lbl,
        )

    def _resolve_path(
        self, root: str, explicit: Optional[str], split: str, subdir: str
    ) -> str:
        if explicit:
            return explicit
        candidate = os.path.join(root, split, subdir)
        if os.path.isdir(candidate):
            return candidate
        return ""

    def _count_images(self, directory: str) -> int:
        if not directory or not os.path.isdir(directory):
            return 0
        count = 0
        for fname in os.listdir(directory):
            ext = os.path.splitext(fname)[1].lower()
            if ext in SUPPORTED_IMG_FORMATS:
                count += 1
        return count

    def _count_labels(self, directory: str) -> int:
        if not directory or not os.path.isdir(directory):
            return 0
        count = 0
        for fname in os.listdir(directory):
            if fname.endswith(YOLO_LABEL_EXT):
                count += 1
        return count

    def _validate_labels(self, directory: str, info: DatasetInfo) -> None:
        if not directory or not os.path.isdir(directory):
            return
        for fname in os.listdir(directory):
            if not fname.endswith(YOLO_LABEL_EXT):
                continue
            path = os.path.join(directory, fname)
            try:
                with open(path, "r") as f:
                    lines = f.readlines()
                stripped = [l.strip() for l in lines if l.strip()]
                if not stripped:
                    info.invalid_labels.append(fname)
                    continue
                for line in stripped:
                    parts = line.split()
                    if len(parts) != 5:
                        info.invalid_labels.append(fname)
                        break
                    cls_id = int(parts[0])
                    vals = [float(p) for p in parts[1:]]
                    if cls_id < 0 or not all(0 <= v <= 1 for v in vals):
                        info.invalid_labels.append(fname)
                        break
            except Exception:
                info.invalid_labels.append(fname)

    def validate(self, info: DatasetInfo) -> List[str]:
        issues = []
        if info.total_images == 0:
            issues.append("No images found in dataset")
        if info.total_labels == 0:
            issues.append("No labels found in dataset")
        if info.invalid_labels:
            issues.append(f"{len(info.invalid_labels)} invalid labels found")
        if info.missing_labels:
            issues.append(f"{len(info.missing_labels)} missing labels")
        if not info.has_valid_labels:
            issues.append("Dataset has invalid or missing labels")
        return issues
