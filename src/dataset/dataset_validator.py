import re
from pathlib import Path
from typing import Optional

from PIL import Image

VERSION_CLASS_MAP = {
    "V1-0": {0},
    "V1-1": {0},
    "V2-0": {0, 1},
    "V2-1": {0, 1, 2},
    "V3-0": {0, 1, 2, 3, 4},
}

NAMING_REGEX = re.compile(r"^[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*_\d{3}_V\d+-\d+$")
SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"})
LABEL_EXTENSION = ".txt"
DEFAULT_SPLITS = ["train", "val", "test"]

MIN_WIDTH = 320
MIN_HEIGHT = 320
MAX_WIDTH = 4096
MAX_HEIGHT = 4096
MIN_FILE_SIZE = 10 * 1024
MAX_FILE_SIZE = 10 * 1024 * 1024


class DatasetValidator:
    """Validate dataset structure, labels, images, naming, and split integrity."""

    def __init__(self, dataset_root: str | Path, version: str = "V1-0"):
        self.root = Path(dataset_root)
        self.version = version
        self.allowed_classes = VERSION_CLASS_MAP.get(version, VERSION_CLASS_MAP["V1-0"])

    def validate_all(self, splits: Optional[list[str]] = None) -> dict:
        """Run all validations and return combined results."""
        if splits is None:
            splits = DEFAULT_SPLITS

        results = {
            "structure": self.validate_structure(),
            "labels": {},
            "images": {},
            "naming": {},
            "split_integrity": self.validate_split_integrity(splits),
        }

        for split in splits:
            results["labels"][split] = self.validate_labels(split)
            results["images"][split] = self.validate_images(split)
            results["naming"][split] = self.validate_naming(split)

        total_errors = 0
        total_warnings = 0

        for item in results["structure"]:
            if item["level"] == "error":
                total_errors += 1
            elif item["level"] == "warning":
                total_warnings += 1

        for item in results["split_integrity"]:
            if item["level"] == "error":
                total_errors += 1
            elif item["level"] == "warning":
                total_warnings += 1

        for split in splits:
            for item in results["labels"][split]:
                if item["level"] == "error":
                    total_errors += 1
                elif item["level"] == "warning":
                    total_warnings += 1
            for item in results["images"][split]:
                if item["level"] == "error":
                    total_errors += 1
                elif item["level"] == "warning":
                    total_warnings += 1
            for item in results["naming"][split]:
                if item["level"] == "error":
                    total_errors += 1
                elif item["level"] == "warning":
                    total_warnings += 1

        results["summary"] = {
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "passed": total_errors == 0,
        }

        return results

    def validate_structure(self) -> list[dict]:
        """Validate that the expected folder structure exists."""
        issues = []
        raw_dir = self.root / "raw"

        if not raw_dir.exists():
            return [{"level": "error", "type": "structure", "message": "Missing directory: raw/"}]

        for split in DEFAULT_SPLITS:
            images_dir = raw_dir / split / "images"
            labels_dir = raw_dir / split / "labels"

            if not images_dir.exists():
                issues.append({
                    "level": "warning",
                    "type": "structure",
                    "message": f"Missing directory: raw/{split}/images/",
                })

            if not labels_dir.exists():
                issues.append({
                    "level": "warning",
                    "type": "structure",
                    "message": f"Missing directory: raw/{split}/labels/",
                })

        return issues

    def validate_labels(self, split: str) -> list[dict]:
        """Validate YOLO label files in a split."""
        issues = []
        labels_dir = self.root / "raw" / split / "labels"

        if not labels_dir.exists():
            return issues

        for label_file in sorted(labels_dir.iterdir()):
            if not label_file.is_file() or label_file.suffix.lower() != LABEL_EXTENSION:
                continue

            with open(label_file) as f:
                lines = f.readlines()

            has_content = False
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                has_content = True

                parts = line.split()
                if len(parts) != 5:
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"Invalid format: expected 5 values, got {len(parts)}",
                    })
                    continue

                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                except ValueError:
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"Non-numeric values: {line}",
                    })
                    continue

                if class_id not in self.allowed_classes:
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"Class ID {class_id} not allowed for version {self.version}",
                    })

                if not (0 <= x_center <= 1):
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"x_center out of range [0,1]: {x_center}",
                    })

                if not (0 <= y_center <= 1):
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"y_center out of range [0,1]: {y_center}",
                    })

                if not (0 < width <= 1):
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"width out of range (0,1]: {width}",
                    })

                if not (0 < height <= 1):
                    issues.append({
                        "level": "error",
                        "type": "label",
                        "file": label_file.name,
                        "line": line_num,
                        "message": f"height out of range (0,1]: {height}",
                    })

            if not has_content:
                issues.append({
                    "level": "warning",
                    "type": "label",
                    "file": label_file.name,
                    "line": 0,
                    "message": "Empty label file",
                })

        return issues

    def validate_images(self, split: str) -> list[dict]:
        """Validate image dimensions and file sizes in a split."""
        issues = []
        images_dir = self.root / "raw" / split / "images"

        if not images_dir.exists():
            return issues

        for image_file in sorted(images_dir.iterdir()):
            if not image_file.is_file():
                continue
            ext = image_file.suffix.lower()
            if ext not in SUPPORTED_IMAGE_EXTENSIONS:
                continue

            file_size = image_file.stat().st_size
            if file_size < MIN_FILE_SIZE:
                issues.append({
                    "level": "warning",
                    "type": "image",
                    "file": image_file.name,
                    "message": f"File size too small: {file_size} bytes (min {MIN_FILE_SIZE})",
                })
            elif file_size > MAX_FILE_SIZE:
                issues.append({
                    "level": "warning",
                    "type": "image",
                    "file": image_file.name,
                    "message": f"File size too large: {file_size} bytes (max {MAX_FILE_SIZE})",
                })

            try:
                with Image.open(image_file) as img:
                    width, height = img.size

                    if width < MIN_WIDTH or height < MIN_HEIGHT:
                        issues.append({
                            "level": "error",
                            "type": "image",
                            "file": image_file.name,
                            "message": f"Image too small: {width}x{height} (min {MIN_WIDTH}x{MIN_HEIGHT})",
                        })

                    if width > MAX_WIDTH or height > MAX_HEIGHT:
                        issues.append({
                            "level": "error",
                            "type": "image",
                            "file": image_file.name,
                            "message": f"Image too large: {width}x{height} (max {MAX_WIDTH}x{MAX_HEIGHT})",
                        })

            except Exception as e:
                issues.append({
                    "level": "error",
                    "type": "image",
                    "file": image_file.name,
                    "message": f"Cannot open image: {e}",
                })

        return issues

    def validate_naming(self, split: str) -> list[dict]:
        """Validate that image files follow the naming convention."""
        issues = []
        images_dir = self.root / "raw" / split / "images"

        if not images_dir.exists():
            return issues

        for f in sorted(images_dir.iterdir()):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext not in SUPPORTED_IMAGE_EXTENSIONS:
                continue

            stem = f.stem
            if not NAMING_REGEX.match(stem):
                issues.append({
                    "level": "error",
                    "type": "naming",
                    "file": f.name,
                    "message": f"Does not match naming convention: {stem}",
                })

        return issues

    def validate_split_integrity(self, splits: list[str]) -> list[dict]:
        """Check that no image stem appears in multiple splits."""
        issues = []
        stem_map = {}

        for split in splits:
            images_dir = self.root / "raw" / split / "images"
            if not images_dir.exists():
                continue

            for f in images_dir.iterdir():
                if not f.is_file():
                    continue
                ext = f.suffix.lower()
                if ext not in SUPPORTED_IMAGE_EXTENSIONS:
                    continue

                stem = f.stem
                if stem not in stem_map:
                    stem_map[stem] = []
                stem_map[stem].append(split)

        for stem, stem_splits in stem_map.items():
            if len(stem_splits) > 1:
                issues.append({
                    "level": "error",
                    "type": "split_integrity",
                    "stem": stem,
                    "splits": stem_splits,
                    "message": f'Stem "{stem}" appears in multiple splits: {", ".join(stem_splits)}',
                })

        return issues
