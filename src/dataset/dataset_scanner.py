import hashlib
from pathlib import Path
from typing import Optional

SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"})
LABEL_EXTENSION = ".txt"
DEFAULT_SPLITS = ["train", "val", "test"]


class DatasetScanner:
    """Scan dataset folders to detect missing files, duplicates, and unsupported formats."""

    def __init__(self, dataset_root: str | Path):
        self.root = Path(dataset_root)

    def scan(self, splits: Optional[list[str]] = None) -> dict:
        """Scan the dataset for issues across specified splits."""
        if splits is None:
            splits = DEFAULT_SPLITS

        all_missing_images = []
        all_missing_labels = []
        all_duplicates = []
        all_unsupported = []
        total_images = 0
        total_labels = 0

        for split in splits:
            result = self._scan_split(split)
            all_missing_images.extend(result["missing_images"])
            all_missing_labels.extend(result["missing_labels"])
            all_duplicates.extend(result["duplicates"])
            all_unsupported.extend(result["unsupported"])
            total_images += result["total_images"]
            total_labels += result["total_labels"]

        return {
            "missing_images": all_missing_images,
            "missing_labels": all_missing_labels,
            "duplicates": all_duplicates,
            "unsupported": all_unsupported,
            "summary": {
                "total_images": total_images,
                "total_labels": total_labels,
                "total_missing_images": len(all_missing_images),
                "total_missing_labels": len(all_missing_labels),
                "total_duplicate_groups": len(all_duplicates),
                "total_unsupported": len(all_unsupported),
            },
        }

    def _scan_split(self, split: str) -> dict:
        """Scan a single split for issues."""
        images_dir = self.root / "raw" / split / "images"
        labels_dir = self.root / "raw" / split / "labels"

        valid_images = []
        unsupported = []

        if images_dir.exists():
            for f in images_dir.iterdir():
                if not f.is_file() or f.name.startswith("."):
                    continue
                ext = f.suffix.lower()
                if ext in SUPPORTED_IMAGE_EXTENSIONS:
                    valid_images.append(f)
                else:
                    unsupported.append({"path": str(f), "extension": ext})

        label_map = {}
        if labels_dir.exists():
            for f in labels_dir.iterdir():
                if f.is_file() and f.suffix.lower() == LABEL_EXTENSION:
                    label_map[f.stem] = f

        image_stems = {}
        for f in valid_images:
            stem = f.stem
            if stem not in image_stems:
                image_stems[stem] = []
            image_stems[stem].append(f)

        missing_labels = []
        for stem in image_stems:
            if stem not in label_map:
                missing_labels.append({
                    "stem": stem,
                    "split": split,
                    "image_paths": [str(p) for p in image_stems[stem]],
                })

        missing_images = []
        for stem in label_map:
            if stem not in image_stems:
                missing_images.append({
                    "stem": stem,
                    "split": split,
                    "label_path": str(label_map[stem]),
                })

        hash_map = {}
        for f in valid_images:
            file_hash = self._compute_hash(f)
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            hash_map[file_hash].append(str(f))

        duplicates = [
            {"hash": h, "files": files}
            for h, files in hash_map.items()
            if len(files) > 1
        ]

        return {
            "missing_images": missing_images,
            "missing_labels": missing_labels,
            "duplicates": duplicates,
            "unsupported": unsupported,
            "total_images": len(valid_images),
            "total_labels": len(label_map),
        }

    @staticmethod
    def _compute_hash(filepath: Path, chunk_size: int = 8192) -> str:
        """Compute SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
