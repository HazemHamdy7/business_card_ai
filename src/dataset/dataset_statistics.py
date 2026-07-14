from pathlib import Path
from typing import Optional

from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"})
DEFAULT_SPLITS = ["train", "val", "test"]

ASPECT_RATIO_BUCKETS = {
    "ultrawide": (2.1, float("inf")),
    "16:9": (1.7, 2.1),
    "5:3": (1.6, 1.7),
    "3:2": (1.45, 1.6),
    "4:3": (1.25, 1.45),
    "1:1": (0.95, 1.25),
    "3:4": (0.72, 0.90),
    "2:3": (0.62, 0.72),
    "9:16": (0.50, 0.62),
    "portrait_ultrawide": (0.0, 0.50),
}


def _categorize_aspect_ratio(width: int, height: int) -> str:
    """Categorize an image's aspect ratio into a named bucket."""
    if height == 0:
        return "unknown"
    ratio = width / height
    for bucket, (low, high) in ASPECT_RATIO_BUCKETS.items():
        if low <= ratio < high:
            return bucket
    return "other"


class DatasetStatistics:
    """Compute dataset statistics including counts, sizes, resolutions, and distributions."""

    def __init__(self, dataset_root: str | Path):
        self.root = Path(dataset_root)

    def compute(self, splits: Optional[list[str]] = None) -> dict:
        """Compute full dataset statistics across specified splits."""
        if splits is None:
            splits = DEFAULT_SPLITS

        per_split = {}
        for split in splits:
            per_split[split] = self._analyze_split(split)

        total_images = sum(s["image_count"] for s in per_split.values())
        total_labels = sum(s["label_count"] for s in per_split.values())
        total_size = sum(s["total_size_bytes"] for s in per_split.values())
        total_annotations = sum(s["total_annotations"] for s in per_split.values())

        all_widths = []
        all_heights = []
        all_aspects: dict[str, int] = {}
        for s in per_split.values():
            all_widths.extend(s["widths"])
            all_heights.extend(s["heights"])
            for bucket, count in s["aspect_ratio_distribution"].items():
                all_aspects[bucket] = all_aspects.get(bucket, 0) + count

        avg_width = round(sum(all_widths) / len(all_widths)) if all_widths else 0
        avg_height = round(sum(all_heights) / len(all_heights)) if all_heights else 0

        return {
            "images": {
                "total": total_images,
                "per_split": {split: per_split[split]["image_count"] for split in splits},
            },
            "labels": {
                "total": total_labels,
                "per_split": {split: per_split[split]["label_count"] for split in splits},
                "total_annotations": total_annotations,
                "per_split_annotations": {
                    split: per_split[split]["total_annotations"] for split in splits
                },
            },
            "dataset_size_bytes": total_size,
            "dataset_size_mb": round(total_size / (1024 * 1024), 2),
            "average_resolution": {"width": avg_width, "height": avg_height},
            "resolution_range": {
                "width": {
                    "min": min(all_widths),
                    "max": max(all_widths),
                }
                if all_widths
                else {"min": 0, "max": 0},
                "height": {
                    "min": min(all_heights),
                    "max": max(all_heights),
                }
                if all_heights
                else {"min": 0, "max": 0},
            },
            "aspect_ratio_distribution": dict(sorted(all_aspects.items())),
            "per_split": {
                split: {
                    "image_count": per_split[split]["image_count"],
                    "label_count": per_split[split]["label_count"],
                    "total_size_bytes": per_split[split]["total_size_bytes"],
                    "total_annotations": per_split[split]["total_annotations"],
                    "aspect_ratio_distribution": per_split[split]["aspect_ratio_distribution"],
                }
                for split in splits
            },
        }

    def _analyze_split(self, split: str) -> dict:
        """Analyze a single split and return raw metrics."""
        images_dir = self.root / "raw" / split / "images"
        labels_dir = self.root / "raw" / split / "labels"

        image_files = []
        if images_dir.exists():
            image_files = [
                f
                for f in images_dir.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
            ]

        label_count = 0
        if labels_dir.exists():
            label_count = len([
                f
                for f in labels_dir.iterdir()
                if f.is_file() and f.suffix.lower() == ".txt"
            ])

        widths: list[int] = []
        heights: list[int] = []
        aspect_dist: dict[str, int] = {}
        total_size = 0
        total_annotations = 0

        for image_file in image_files:
            total_size += image_file.stat().st_size
            try:
                with Image.open(image_file) as img:
                    w, h = img.size
                    widths.append(w)
                    heights.append(h)
                    bucket = _categorize_aspect_ratio(w, h)
                    aspect_dist[bucket] = aspect_dist.get(bucket, 0) + 1
            except Exception:
                pass

        if labels_dir.exists():
            for label_file in labels_dir.iterdir():
                if label_file.is_file() and label_file.suffix.lower() == ".txt":
                    try:
                        with open(label_file) as f:
                            total_annotations += sum(1 for line in f if line.strip())
                    except Exception:
                        pass

        return {
            "image_count": len(image_files),
            "label_count": label_count,
            "total_size_bytes": total_size,
            "total_annotations": total_annotations,
            "widths": widths,
            "heights": heights,
            "aspect_ratio_distribution": dict(sorted(aspect_dist.items())),
        }
