from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .dataset_balance import BalanceReport, DatasetBalance
from .dataset_health import DatasetHealth, HealthReport
from .dataset_quality import DatasetQuality, QualityResult


@dataclass
class ReadinessResult:
    status: str = "NOT_READY"
    reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    health: Optional[HealthReport] = None
    balance: Optional[BalanceReport] = None
    quality: Optional[QualityResult] = None

    @property
    def is_ready(self) -> bool:
        return self.status == "READY"


class DatasetReadiness:
    MIN_QUALITY_SCORE = 70.0
    MAX_IMBALANCE_SCORE = 0.5
    MIN_CLASSES = 1
    MIN_IMAGES_PER_CLASS = 10

    def __init__(
        self,
        class_names: Optional[Dict[int, str]] = None,
        min_quality_score: float = 70.0,
        max_imbalance_score: float = 0.5,
        min_images_per_class: int = 10,
    ):
        self.class_names = class_names or {}
        self.min_quality_score = min_quality_score
        self.max_imbalance_score = max_imbalance_score
        self.min_images_per_class = min_images_per_class

    def evaluate(
        self,
        dataset_root: str,
        train_label_dir: Optional[str] = None,
        val_label_dir: Optional[str] = None,
        test_label_dir: Optional[str] = None,
        image_dir: Optional[str] = None,
        export_dir: Optional[str] = None,
    ) -> ReadinessResult:
        result = ReadinessResult()
        reasons: List[str] = []
        blocking: List[str] = []

        quality = DatasetQuality()
        quality_result = quality.evaluate(
            image_dir=image_dir or dataset_root,
            label_dir=train_label_dir,
        )
        result.quality = quality_result
        result.quality_score = quality_result.overall_score

        health = DatasetHealth()
        health_result = health.analyze(dataset_root, export_dir=export_dir)
        result.health = health_result

        balance = DatasetBalance(class_names=self.class_names)
        balance_result = balance.analyze(
            train_dir=train_label_dir,
            val_dir=val_label_dir,
            test_dir=test_label_dir,
        )
        result.balance = balance_result

        if quality_result.overall_score < self.min_quality_score:
            reasons.append(
                f"Quality score {quality_result.overall_score:.1f} below minimum {self.min_quality_score}"
            )
            blocking.append(
                f"Quality score too low ({quality_result.overall_score:.1f}/{self.min_quality_score})"
            )

        if not health_result.is_healthy:
            reasons.append("Dataset health checks failed")
            for issue in health_result.issues[:3]:
                blocking.append(issue)

        if balance_result.imbalance_score > self.max_imbalance_score:
            reasons.append(
                f"Class imbalance {balance_result.imbalance_score:.2f} exceeds max {self.max_imbalance_score}"
            )
            blocking.append(f"Class imbalance too high ({balance_result.imbalance_score:.2f})")

        total_images = balance_result.total_images
        num_classes = balance_result.num_classes

        if num_classes < self.MIN_CLASSES:
            reasons.append(f"Too few classes ({num_classes} < {self.MIN_CLASSES})")
            blocking.append(f"Only {num_classes} classes found")

        if total_images < 10:
            reasons.append(f"Too few images ({total_images} < 10)")
            blocking.append(f"Only {total_images} images available")

        for cls_name, count in balance_result.images_per_class.items():
            if count < self.min_images_per_class:
                reasons.append(
                    f"Class '{cls_name}' has only {count} images (min {self.min_images_per_class})"
                )

        if quality_result.corrupted_images:
            reasons.append(f"{len(quality_result.corrupted_images)} corrupted images found")
            blocking.append(f"{len(quality_result.corrupted_images)} corrupted images")

        if quality_result.missing_labels:
            reasons.append(f"{len(quality_result.missing_labels)} missing labels")
            blocking.append(f"{len(quality_result.missing_labels)} missing labels")

        recommendations: List[str] = []
        if quality_result.overall_score < self.min_quality_score:
            recommendations.append("Improve image quality and label completeness")
        if balance_result.imbalance_score > self.max_imbalance_score:
            recommendations.append("Balance class distribution with augmentation or undersampling")
        if quality_result.corrupted_images:
            recommendations.append("Remove or replace corrupted images")
        if quality_result.missing_labels:
            recommendations.append("Add missing labels for all images")
        if not health_result.folder_structure_ok:
            recommendations.append("Fix dataset folder structure (train/val/test with images/labels subdirs)")
        if total_images < 100:
            recommendations.append("Collect more data for better model generalization")

        if not blocking:
            result.status = "READY"
        else:
            result.status = "NOT_READY"

        result.reasons = reasons
        result.recommendations = recommendations
        result.blocking_issues = blocking

        return result
