import json
import shutil
from pathlib import Path
from typing import Optional

from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"})
DEFAULT_SPLITS = ["train", "val", "test"]


class DatasetExporter:
    """Export dataset to different formats (YOLO, COCO)."""

    def __init__(self, dataset_root: str | Path):
        self.root = Path(dataset_root)

    def export_yolo(
        self,
        output_dir: str | Path,
        splits: Optional[list[str]] = None,
        source: str = "raw",
    ) -> Path:
        """Export dataset in YOLO format (copies images and labels)."""
        if splits is None:
            splits = DEFAULT_SPLITS

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        for split in splits:
            src_images = self.root / source / split / "images"
            src_labels = self.root / source / split / "labels"
            dst_images = output / split / "images"
            dst_labels = output / split / "labels"

            if src_images.exists():
                dst_images.mkdir(parents=True, exist_ok=True)
                for f in src_images.iterdir():
                    if f.is_file() and f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                        shutil.copy2(f, dst_images / f.name)

            if src_labels.exists():
                dst_labels.mkdir(parents=True, exist_ok=True)
                for f in src_labels.iterdir():
                    if f.is_file() and f.suffix.lower() == ".txt":
                        shutil.copy2(f, dst_labels / f.name)

        return output

    def export_coco(
        self,
        output_dir: str | Path,
        splits: Optional[list[str]] = None,
        source: str = "raw",
    ) -> Path:
        """Export dataset in COCO JSON format."""
        if splits is None:
            splits = DEFAULT_SPLITS

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        categories = [
            {"id": 0, "name": "business_card", "supercategory": "object"},
        ]

        for split in splits:
            src_images = self.root / source / split / "images"
            src_labels = self.root / source / split / "labels"
            dst_images = output / split / "images"

            if src_images.exists():
                dst_images.mkdir(parents=True, exist_ok=True)

            coco_data: dict = {
                "images": [],
                "annotations": [],
                "categories": categories,
            }
            annotation_id = 1
            image_id = 1

            if src_images.exists():
                for img_file in sorted(src_images.iterdir()):
                    if not img_file.is_file() or img_file.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                        continue

                    shutil.copy2(img_file, dst_images / img_file.name)

                    try:
                        with Image.open(img_file) as img:
                            width, height = img.size
                    except Exception:
                        width, height = 0, 0

                    coco_data["images"].append({
                        "id": image_id,
                        "file_name": img_file.name,
                        "width": width,
                        "height": height,
                    })

                    label_file = src_labels / f"{img_file.stem}.txt"
                    if label_file.exists():
                        try:
                            with open(label_file) as f:
                                for line in f:
                                    line = line.strip()
                                    if not line:
                                        continue
                                    parts = line.split()
                                    if len(parts) != 5:
                                        continue

                                    class_id = int(parts[0])
                                    x_center = float(parts[1])
                                    y_center = float(parts[2])
                                    bw = float(parts[3])
                                    bh = float(parts[4])

                                    abs_x = (x_center - bw / 2) * width
                                    abs_y = (y_center - bh / 2) * height
                                    abs_w = bw * width
                                    abs_h = bh * height

                                    coco_data["annotations"].append({
                                        "id": annotation_id,
                                        "image_id": image_id,
                                        "category_id": class_id,
                                        "bbox": [
                                            round(abs_x, 2),
                                            round(abs_y, 2),
                                            round(abs_w, 2),
                                            round(abs_h, 2),
                                        ],
                                        "area": round(abs_w * abs_h, 2),
                                        "iscrowd": 0,
                                    })
                                    annotation_id += 1
                        except Exception:
                            pass

                    image_id += 1

            json_path = output / f"{split}_annotations.json"
            with open(json_path, "w") as f:
                json.dump(coco_data, f, indent=2)

        return output

    def export_split(
        self,
        split: str,
        output_dir: str | Path,
        source: str = "raw",
    ) -> Path:
        """Export a single split to the output directory."""
        output = Path(output_dir) / split
        output.mkdir(parents=True, exist_ok=True)

        src_images = self.root / source / split / "images"
        src_labels = self.root / source / split / "labels"

        if src_images.exists():
            dst_images = output / "images"
            dst_images.mkdir(parents=True, exist_ok=True)
            for f in src_images.iterdir():
                if f.is_file() and f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    shutil.copy2(f, dst_images / f.name)

        if src_labels.exists():
            dst_labels = output / "labels"
            dst_labels.mkdir(parents=True, exist_ok=True)
            for f in src_labels.iterdir():
                if f.is_file() and f.suffix.lower() == ".txt":
                    shutil.copy2(f, dst_labels / f.name)

        return output
