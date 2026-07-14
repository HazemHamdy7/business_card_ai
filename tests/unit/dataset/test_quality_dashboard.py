import json
import os
import tempfile

import pytest

from src.dataset.quality_dashboard import QualityDashboard
from src.dataset.dataset_readiness import ReadinessResult
from src.dataset.dataset_quality import QualityResult
from src.dataset.dataset_health import HealthReport
from src.dataset.dataset_balance import BalanceReport


class TestQualityDashboard:
    def make_readiness_result(self, status="READY"):
        quality = QualityResult(
            overall_score=85.0,
            total_images=100,
            total_labels=95,
            total_valid=98,
        )
        health = HealthReport(
            is_healthy=True,
            total_images=100,
            total_labels=95,
        )
        balance = BalanceReport(
            total_objects=200,
            total_images=100,
            num_classes=3,
            imbalance_score=0.2,
            objects_per_class={"card_front": 100, "card_back": 60, "side_view": 40},
            split_distribution={"train": 70, "val": 20, "test": 10},
        )
        return ReadinessResult(
            status=status,
            quality_score=85.0,
            reasons=[],
            recommendations=["Add more data"],
            blocking_issues=[],
            quality=quality,
            health=health,
            balance=balance,
        )

    def test_generate_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = QualityDashboard()
            readiness = self.make_readiness_result()
            path = dashboard.generate_json(readiness, tmp)
            assert os.path.exists(path)
            with open(path, "r") as f:
                data = json.load(f)
            assert data["readiness"]["status"] == "READY"
            assert data["quality"]["overall_score"] == 85.0

    def test_generate_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = QualityDashboard()
            readiness = self.make_readiness_result()
            path = dashboard.generate_markdown(readiness, tmp)
            assert os.path.exists(path)
            with open(path, "r") as f:
                content = f.read()
            assert "Dataset Quality Dashboard" in content
            assert "READY" in content

    def test_generate_markdown_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = QualityDashboard()
            readiness = self.make_readiness_result(status="NOT_READY")
            readiness.blocking_issues = ["Missing labels"]
            readiness.reasons = ["Low quality"]
            path = dashboard.generate_markdown(readiness, tmp)
            with open(path, "r") as f:
                content = f.read()
            assert "NOT_READY" in content
            assert "Missing labels" in content

    def test_generate_summary(self):
        dashboard = QualityDashboard()
        readiness = self.make_readiness_result()
        summary = dashboard.generate_summary(readiness)
        assert "READY" in summary
        assert "85.0" in summary

    def test_generate_summary_not_ready(self):
        dashboard = QualityDashboard()
        readiness = self.make_readiness_result(status="NOT_READY")
        readiness.blocking_issues = ["Corrupted images"]
        summary = dashboard.generate_summary(readiness)
        assert "NOT_READY" in summary
