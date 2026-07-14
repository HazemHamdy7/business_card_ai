# Annotation Studio

Annotation infrastructure for Business Card Detection — validates YOLO format labels, inspects annotation quality, checks dataset consistency, generates statistics, and exports comprehensive reports.

## Modules

### AnnotationValidator

Validates individual YOLO-format annotation files.

```python
from src.annotations import AnnotationValidator

validator = AnnotationValidator(allowed_classes=[0, 1, 2])
result = validator.validate_file("path/to/label.txt")

result.is_valid      # True if all lines are valid
result.total_objects # count of valid annotations
result.is_empty      # True if file has no content
result.line_results  # per-line validation details
result.errors        # file-level error messages
```

YOLO format expected: `<class_id> <x_center> <y_center> <width> <height>` (normalized 0-1, one box per line).

### LabelInspector

Scans a label directory for issues: missing/orphaned annotations, invalid class IDs, out-of-bound coordinates, empty files.

```python
from src.annotations import LabelInspector

inspector = LabelInspector(allowed_classes=[0, 1])
result = inspector.inspect(label_dir="labels/", image_dir="images/")

result.missing_labels      # images without labels
result.orphaned_labels     # labels without images
result.empty_labels        # label files with no content
result.invalid_class_ids   # class IDs out of allowed range
result.out_of_bounds_files # files with OOB coordinates
result.issues_found        # True if any issues detected
```

### DatasetConsistencyChecker

Verifies image-label pairing and computes class distribution across paired files.

```python
from src.annotations import DatasetConsistencyChecker

checker = DatasetConsistencyChecker(allowed_classes=[0, 1])
result = checker.check(
    label_dir="labels/",
    image_dir="images/",
    class_names={0: "card_front", 1: "card_back"},
)

result.is_consistent       # True if all images have labels and vice versa
result.paired              # count of matched image-label pairs
result.class_distribution  # dict of class_id -> count
result.unmatched_images    # images without corresponding labels
result.unmatched_labels    # labels without corresponding images
```

### AnnotationStatistics

Computes dataset-wide annotation statistics including class distribution, bounding box dimensions, objects per image, and aspect ratio distribution.

```python
from src.annotations import AnnotationStatistics

stats = AnnotationStatistics(allowed_classes=[0, 1])
result = stats.compute(label_dir="labels/")

result.total_objects
result.objects_per_image_stats  # PerImageStats(min, max, mean, median, std)
result.class_distribution       # {class_id: count}
result.bbox_width_stats         # BboxDimensionStats(min, max, mean, median, std)
result.bbox_height_stats
result.bbox_area_stats
result.aspect_ratio_buckets     # ultra_wide / wide / square / tall / ultra_tall
```

### AnnotationExporter

Exports validation, inspection, consistency, and statistics results to JSON, and generates a Markdown summary report.

```python
from src.annotations import AnnotationExporter

exporter = AnnotationExporter()

exporter.export_validation_to_json(results, "validation.json")
exporter.export_inspection_to_json(result, "inspection.json")
exporter.export_consistency_to_json(result, "consistency.json")
exporter.export_statistics_to_json(result, "statistics.json")

markdown = exporter.export_summary_to_markdown(
    stats=stats_result,
    consistency=consistency_result,
    inspection=inspection_result,
    output_path="annotation_summary.md",
)
```

### AnnotationManager

Central orchestrator that runs all validation, inspection, consistency checks, statistics, and exports in one call.

```python
from src.annotations import AnnotationManager

manager = AnnotationManager(
    allowed_classes=[0, 1, 2],
    class_names={0: "card_front", 1: "card_back", 2: "side_view"},
)
report = manager.run(
    label_dir="labels/",
    image_dir="images/",
    export_dir="reports/",
)

report.total_valid_files
report.total_invalid_files
report.total_objects
report.issues_found
report.validated_files      # List[AnnotationValidationResult]
report.inspection           # LabelInspectionResult
report.consistency          # ConsistencyResult
report.statistics           # AnnotationStatsResult
report.export_paths         # Dict[str, str] of generated file paths
```

## Data Flow

```
Labels/Images
     |
     v
AnnotationManager.run()
     |
     +-- AnnotationValidator    -> validation results
     +-- LabelInspector         -> inspection report
     +-- DatasetConsistencyChecker -> consistency report
     +-- AnnotationStatistics   -> statistics
     |
     v
AnnotationExporter -> JSON reports + Markdown summary
```

## Validation Rules

- Each line must have exactly 5 space-separated values
- `class_id`: integer, 0–999
- `x_center`, `y_center`, `width`, `height`: floats in [0, 1]
- `width`, `height`: must be positive (> 0)
- Blank lines are tolerated and skipped
- Lines with 5 values where all are valid pass; partial failures are reported per line

## Class ID Validation

- Default range: 0–999
- Optional `allowed_classes` list restricts valid class IDs
- Violations are reported by both `AnnotationValidator` and `LabelInspector`

## Output Files

When `export_dir` is provided, the manager generates:

| File | Contents |
|------|----------|
| `validation.json` | Per-file and per-line validation results |
| `inspection.json` | Missing/orphaned/empty/invalid labels report |
| `consistency.json` | Pairing status and class distribution |
| `statistics.json` | Dataset-wide annotation statistics |
| `annotation_summary.md` | Human-readable Markdown summary |
