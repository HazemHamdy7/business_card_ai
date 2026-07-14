from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentRecord:
    experiment_id: str
    created_at: str = ""
    updated_at: str = ""
    status: str = "created"
    config: Dict[str, Any] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    hardware: Dict[str, Any] = field(default_factory=dict)
    software: Dict[str, Any] = field(default_factory=dict)
    execution_time_seconds: float = 0.0
    total_epochs: int = 0
    completed_epochs: int = 0
    best_score: float = 0.0
    loss_history: List[float] = field(default_factory=list)
    metrics_history: Dict[str, List[float]] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_summary(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "total_epochs": self.total_epochs,
            "completed_epochs": self.completed_epochs,
            "best_score": self.best_score,
            "execution_time_seconds": self.execution_time_seconds,
        }


class ExperimentTracker:
    def __init__(self, output_dir: str = "experiments"):
        self._output_dir = output_dir
        self._records: Dict[str, ExperimentRecord] = {}
        os.makedirs(output_dir, exist_ok=True)

    def create_experiment(
        self,
        experiment_id: str,
        config: Optional[Dict[str, Any]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> ExperimentRecord:
        now = datetime.now().isoformat()
        record = ExperimentRecord(
            experiment_id=experiment_id,
            created_at=now,
            updated_at=now,
            status="created",
            config=config or {},
            hyperparameters=hyperparameters or {},
            software=self._get_software_versions(),
        )
        self._records[experiment_id] = record
        self._save_json(record)
        return record

    def start_experiment(self, experiment_id: str) -> None:
        record = self._get_record(experiment_id)
        record.status = "running"
        record.updated_at = datetime.now().isoformat()
        self._save_json(record)

    def complete_experiment(
        self,
        experiment_id: str,
        execution_time: float = 0.0,
        best_score: float = 0.0,
    ) -> None:
        record = self._get_record(experiment_id)
        record.status = "completed"
        record.execution_time_seconds = execution_time
        record.best_score = best_score
        record.updated_at = datetime.now().isoformat()
        self._save_json(record)

    def fail_experiment(
        self,
        experiment_id: str,
        error: str = "",
    ) -> None:
        record = self._get_record(experiment_id)
        record.status = "failed"
        record.notes = error
        record.updated_at = datetime.now().isoformat()
        self._save_json(record)

    def log_epoch(
        self,
        experiment_id: str,
        epoch: int,
        loss: float,
        metrics: Optional[Dict[str, float]] = None,
    ) -> None:
        record = self._get_record(experiment_id)
        record.loss_history.append(loss)
        record.completed_epochs = epoch
        if metrics:
            for key, value in metrics.items():
                if key not in record.metrics_history:
                    record.metrics_history[key] = []
                record.metrics_history[key].append(value)
        record.updated_at = datetime.now().isoformat()
        self._save_json(record)

    def get_record(self, experiment_id: str) -> Optional[ExperimentRecord]:
        return self._records.get(experiment_id)

    def list_experiments(self) -> List[str]:
        return list(self._records.keys())

    def _get_record(self, experiment_id: str) -> ExperimentRecord:
        if experiment_id not in self._records:
            record = self._load_json(experiment_id)
            if record:
                self._records[experiment_id] = record
                return record
            raise KeyError(f"Experiment '{experiment_id}' not found")
        return self._records[experiment_id]

    def _get_software_versions(self) -> Dict[str, str]:
        versions = {
            "python": _get_python_version(),
        }
        try:
            import torch
            versions["torch"] = torch.__version__
        except ImportError:
            pass
        try:
            import cv2
            versions["opencv"] = cv2.__version__
        except ImportError:
            pass
        try:
            import numpy as np
            versions["numpy"] = np.__version__
        except ImportError:
            pass
        return versions

    def _save_json(self, record: ExperimentRecord) -> str:
        path = os.path.join(
            self._output_dir, f"{record.experiment_id}.json"
        )
        with open(path, "w") as f:
            json.dump(record.to_dict(), f, indent=2)
        return path

    def _load_json(self, experiment_id: str) -> Optional[ExperimentRecord]:
        path = os.path.join(self._output_dir, f"{experiment_id}.json")
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return ExperimentRecord(**data)
        except Exception:
            return None

    def generate_markdown(self, experiment_id: str) -> str:
        record = self._get_record(experiment_id)
        lines = [
            f"# Experiment: {record.experiment_id}",
            "",
            f"**Status:** {record.status}",
            f"**Created:** {record.created_at}",
            f"**Updated:** {record.updated_at}",
            "",
            "## Summary",
            "",
            f"- **Total Epochs:** {record.total_epochs}",
            f"- **Completed Epochs:** {record.completed_epochs}",
            f"- **Best Score:** {record.best_score:.4f}",
            f"- **Execution Time:** {record.execution_time_seconds:.2f}s",
            "",
            "## Hardware",
            "",
        ]
        if record.hardware:
            for key, value in record.hardware.items():
                lines.append(f"- **{key}:** {value}")
        lines.append("")
        lines.append("## Software")
        lines.append("")
        if record.software:
            for key, value in record.software.items():
                lines.append(f"- **{key}:** {value}")
        lines.append("")
        if record.loss_history:
            lines.append("## Loss History")
            lines.append("")
            for i, loss in enumerate(record.loss_history):
                lines.append(f"- Epoch {i+1}: {loss:.6f}")
            lines.append("")
        return "\n".join(lines)


def _get_python_version() -> str:
    import sys
    return sys.version
