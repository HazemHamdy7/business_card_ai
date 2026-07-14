# Dataset Quality & Validation

Production-grade dataset quality analysis, health checking, balance analysis, duplicate detection, and readiness assessment for Business Card Detection training datasets.

## Modules

### DatasetQuality

Evaluates dataset quality across 5 weighted categories, producing an overall score (0–100).

```python
from src.dataset import DatasetQuality

quality = DatasetQuality()
result = quality.evaluate(
    image_dir="path/to/images/",
    label_dir="path/to/labels/",
)

result.overall_score           # 0–100 weighted score
result.label_completeness      # 0–100
result.image_integrity         # 0–100
result.format_compliance       # 0–100
result.resolution_compliance   # 0–100
result.aspect_ratio_compliance # 0–100
result.missing_labels          # files without corresponding labels
result.empty_labels            # label files with no content
result.invalid_labels          # label files with parse errors
result.corrupted_images        # images that could not be decoded
result.unsupported_formats     # files with non-allowed extensions
result.resolution_issues       # images outside resolution bounds
result.aspect_ratio_issues     # images outside aspect ratio bounds
result.total_images            # total image files found
result.total_labels            # images with valid labels
result.total_valid             # images without corruption
```

Custom thresholds via config dict:

```python
config = {
    "min_resolution": [300, 300],
    "max_resolution": [4096, 4096],
    "min_aspect_ratio": 0.5,
    "max_aspect_ratio": 3.0,
    "allowed_formats": [".jpg", ".png", ".jpeg"],
    "weights": {
        "label_completeness": 25,
        "image_integrity": 25,
        "format_compliance": 15,
        "resolution_compliance": 20,
        "aspect_ratio_compliance": 15,
    },
}
quality = DatasetQuality(config=config)
```

### DatasetHealth

Analyzes dataset integrity including folder structure, annotation pairing, image readability, and export completeness.

```python
from src.dataset import DatasetHealth

health = DatasetHealth()
report = health.analyze(
    dataset_root="path/to/dataset/",
    export_dir="path/to/exports/",
)

report.is_healthy              # True if all checks pass
report.folder_structure_ok     # train/val/test + images/labels
report.annotation_integrity_ok # all images have labels, no orphans
report.image_integrity_ok      # all images are readable
report.export_integrity_ok     # required export files exist
report.folder_structure_issues
report.annotation_integrity_issues
report.image_integrity_issues
report.export_integrity_issues
report.total_images
report.total_labels
```

Expected folder structure:

```
dataset_root/
├── train/
│   ├── images/
│   │   ├── img001.jpg
│   │   └── ...
│   └── labels/
│       ├── img001.txt
│       └── ...
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

### DatasetBalance

Analyzes class distribution, objects per class, and split balance across training/validation/test sets.

```python
from src.dataset import DatasetBalance

balance = DatasetBalance(class_names={0: "card_front", 1: "card_back"})
report = balance.analyze(
    train_dir="path/to/train/labels/",
    val_dir="path/to/val/labels/",
    test_dir="path/to/test/labels/",
)

report.objects_per_class    # {class_name: total_object_count}
report.images_per_class     # {class_name: total_image_count}
report.split_distribution   # {split_name: label_file_count}
report.imbalance_score      # 0.0 (perfect) to 1.0 (worst)
report.total_objects        # total annotations across all splits
report.total_images         # total labeled images
report.num_classes          # number of distinct classes
```

### DuplicateDetector

Finds exact duplicates (SHA256) and near-duplicates (perceptual hash) in an image directory.

```python
from src.dataset import DuplicateDetector

detector = DuplicateDetector(hash_size=8, threshold=0.1)
report = detector.find_duplicates("path/to/images/")

report.sha256_duplicates          # [(path1, path2), ...]
report.perceptual_duplicates      # [(path1, path2), ...]
report.near_duplicates            # [(path1, path2, similarity), ...]
report.total_exact_duplicate_pairs
report.total_perceptual_duplicate_pairs
report.total_near_duplicate_pairs
report.unique_images              # images not in any duplicate pair
report.total_images_checked
```

### DatasetReadiness

Combines quality, health, and balance to determine if a dataset is production-ready for AI training.

```python
from src.dataset import DatasetReadiness

readiness = DatasetReadiness(
    class_names={0: "card_front"},
    min_quality_score=70.0,
    max_imbalance_score=0.5,
    min_images_per_class=10,
)
result = readiness.evaluate(
    dataset_root="path/to/dataset/",
    train_label_dir="path/to/train/labels/",
    val_label_dir="path/to/val/labels/",
    test_label_dir="path/to/test/labels/",
    image_dir="path/to/images/",
    export_dir="path/to/exports/",
)

result.status            # "READY" or "NOT_READY"
result.is_ready          # True/False
result.quality_score     # 0–100
result.reasons           # list of issues found
result.recommendations   # actionable suggestions
result.blocking_issues   # critical blockers
result.quality           # QualityResult
result.health            # HealthReport
result.balance           # BalanceReport
```

### QualityDashboard

Generates JSON reports and a human-readable Markdown dashboard.

```python
from src.dataset import QualityDashboard

dashboard = QualityDashboard()

json_path = dashboard.generate_json(readiness, "output_dir/")
# Creates: dataset_quality.json, dataset_health.json

md_path = dashboard.generate_markdown(readiness, "output_dir/")
# Creates: dataset_dashboard.md

summary = dashboard.generate_summary(readiness)
# Returns: human-readable text summary
```

## Quality Score Calculation

The overall quality score is a weighted average of 5 category scores:

| Category | Default Weight | Description |
|----------|----------------|-------------|
| Label Completeness | 25% | Ratio of images with valid labels |
| Image Integrity | 25% | Ratio of decodable images |
| Format Compliance | 15% | Ratio of files with allowed extensions |
| Resolution Compliance | 20% | Ratio of images within resolution bounds |
| Aspect Ratio Compliance | 15% | Ratio of images within aspect ratio bounds |

Each category score = `(valid_count / total_count) × 100`.

## Readiness Criteria

A dataset is marked READY when:

- **Quality score** ≥ 70 (configurable)
- **Class imbalance** ≤ 0.5 (configurable)
- **At least 1 class** present
- **At least 10 images** available
- **No missing labels** for any image
- **No corrupted images**
- **Dataset health checks pass** (folder structure, annotation integrity)
