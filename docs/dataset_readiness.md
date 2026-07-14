# Dataset Readiness

The `DatasetReadiness` module determines whether a dataset is production-ready for AI training by combining quality, health, and balance analyses into a single `READY` / `NOT_READY` verdict.

## Quick Start

```python
from src.dataset import DatasetReadiness

result = DatasetReadiness().evaluate(
    dataset_root="data/dataset/",
    train_label_dir="data/dataset/train/labels/",
    image_dir="data/images/",
)

if result.is_ready:
    print("Dataset is ready for training!")
else:
    print(f"Not ready: {len(result.blocking_issues)} blocking issues")
    for issue in result.blocking_issues:
        print(f"  - {issue}")
    for rec in result.recommendations:
        print(f"  Recommendation: {rec}")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_quality_score` | 70.0 | Minimum overall quality score (0–100) |
| `max_imbalance_score` | 0.5 | Maximum acceptable class imbalance (0–1) |
| `min_images_per_class` | 10 | Minimum images required per class |

## Decision Logic

```
ALL checks must pass for READY:
  ├── Quality score >= min_quality_score (default 70)
  ├── Dataset health is_healthy == True
  ├── Class imbalance <= max_imbalance_score (default 0.5)
  ├── At least 1 class present
  ├── At least 10 total images
  ├── Each class has >= min_images_per_class images
  ├── No corrupted images
  └── No missing labels
```

## Output

```python
result.status            # "READY" or "NOT_READY"
result.is_ready          # bool
result.quality_score     # float 0–100
result.reasons           # List[str] — all issues found
result.recommendations   # List[str] — actionable suggestions
result.blocking_issues   # List[str] — critical blockers
result.quality           # QualityResult from DatasetQuality
result.health            # HealthReport from DatasetHealth
result.balance           # BalanceReport from DatasetBalance
```
