# Dataset Management

## Overview

The dataset management system provides tools for scanning, validating, analyzing, reporting, and exporting the Business Card Detection dataset. It is located in `src/dataset/`.

## Modules

### DatasetScanner

Scans dataset folders to detect issues:

- **Missing images**: Label files without a corresponding image
- **Missing labels**: Image files without a corresponding label
- **Duplicates**: Identical files detected via SHA256 hash
- **Unsupported formats**: Files with extensions outside the supported set (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.tiff`, `.tif`)

```python
from src.dataset import DatasetScanner

scanner = DatasetScanner("dataset/")
result = scanner.scan()  # scans train/val/test by default
result = scanner.scan(splits=["train", "val"])
```

### DatasetValidator

Validates dataset quality:

- **Structure**: Expected directory tree exists (`raw/{split}/{images,labels}`)
- **Labels**: YOLO format correctness, class IDs in range, value bounds
- **Images**: Dimensions (320–4096 px), file size (10 KB–10 MB), integrity
- **Naming**: Convention `BATCH_###_V#-#` or `PREFIX_BATCH_###_V#-#`
- **Split integrity**: No image stem duplicated across splits

```python
from src.dataset import DatasetValidator

validator = DatasetValidator("dataset/", version="V1-0")
result = validator.validate_all()
```

### DatasetStatistics

Computes dataset metrics:

- Image counts per split
- Dataset size (bytes, MB)
- Average resolution
- Resolution range
- Aspect ratio distribution (16:9, 4:3, 3:2, 1:1, etc.)
- Label and annotation counts

```python
from src.dataset import DatasetStatistics

stats = DatasetStatistics("dataset/")
result = stats.compute()
```

### DatasetReport

Generates structured reports:

- `to_json()` — JSON format
- `to_markdown()` — Markdown format
- Accepts scanner, validator, and statistics results

```python
from src.dataset import DatasetReport

report = DatasetReport(
    scanner_result=scan_result,
    validator_result=val_result,
    statistics=stats_result,
)
json_output = report.to_json("report.json")
md_output = report.to_markdown("report.md")
```

### DatasetExporter

Exports dataset to different formats:

- `export_yolo()` — Copies images and labels into YOLO directory structure
- `export_coco()` — Converts YOLO labels to COCO JSON format
- `export_split()` — Exports a single split

```python
from src.dataset import DatasetExporter

exporter = DatasetExporter("dataset/")
exporter.export_yolo("exports/yolo/")
exporter.export_coco("exports/coco/")
```

## Dataset Directory Structure

```
dataset/
└── raw/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
```

## Supported Formats

- **Images**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.tiff`, `.tif`
- **Labels**: `.txt` (YOLO format)

## Naming Convention

```
BCA001_001_V1-0.jpg  →  batch: BCA001, number: 001, version: V1-0
DRC_BCA001_002_V1-0.png  →  prefix: DRC_, batch: BCA001, number: 002, version: V1-0
```

## Validation Standards (V1-0)

| Check | Standard |
|-------|----------|
| Image width | 320 – 4096 px |
| Image height | 320 – 4096 px |
| File size | 10 KB – 10 MB |
| Allowed classes | 0 (business_card) |
| Label format | `<class_id> <x_center> <y_center> <width> <height>` |
| Coordinate range | [0, 1] for centers; (0, 1] for width/height |
