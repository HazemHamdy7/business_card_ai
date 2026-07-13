import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import torch

from src.core.config import ConfigurationManager
from src.core.paths import Paths


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
        }


class HealthCheck:
    def __init__(self, config_manager: ConfigurationManager | None = None) -> None:
        self._config_manager = config_manager or ConfigurationManager()

    def check_cuda(self) -> HealthCheckResult:
        available = torch.cuda.is_available()
        if available:
            try:
                device_name = torch.cuda.get_device_name(0)
                return HealthCheckResult(
                    name="cuda",
                    status=HealthStatus.HEALTHY,
                    message="CUDA is available",
                    details={"device": device_name, "device_count": torch.cuda.device_count()},
                )
            except Exception as e:
                return HealthCheckResult(
                    name="cuda",
                    status=HealthStatus.DEGRADED,
                    message=f"CUDA available but error: {e}",
                )
        return HealthCheckResult(
            name="cuda",
            status=HealthStatus.DEGRADED,
            message="CUDA is not available, running on CPU",
        )

    def check_disk(self) -> HealthCheckResult:
        try:
            root = Paths.root()
            usage = shutil.disk_usage(str(root))
            free_gb = usage.free / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)
            free_percent = (usage.free / usage.total) * 100

            if free_gb < 0.5:
                return HealthCheckResult(
                    name="disk",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Low disk space: {free_gb:.2f} GB free",
                    details={"free_gb": round(free_gb, 2), "total_gb": round(total_gb, 2), "free_percent": round(free_percent, 2)},
                )
            if free_gb < 2.0:
                return HealthCheckResult(
                    name="disk",
                    status=HealthStatus.DEGRADED,
                    message=f"Low disk space: {free_gb:.2f} GB free",
                    details={"free_gb": round(free_gb, 2), "total_gb": round(total_gb, 2), "free_percent": round(free_percent, 2)},
                )
            return HealthCheckResult(
                name="disk",
                status=HealthStatus.HEALTHY,
                message=f"Disk OK: {free_gb:.2f} GB free",
                details={"free_gb": round(free_gb, 2), "total_gb": round(total_gb, 2), "free_percent": round(free_percent, 2)},
            )
        except Exception as e:
            return HealthCheckResult(name="disk", status=HealthStatus.UNHEALTHY, message=f"Disk check failed: {e}")

    def check_configuration(self) -> HealthCheckResult:
        try:
            data = self._config_manager.load()
            if not data:
                return HealthCheckResult(
                    name="configuration",
                    status=HealthStatus.DEGRADED,
                    message="Configuration is empty",
                    details={"keys": list(data.keys())},
                )
            return HealthCheckResult(
                name="configuration",
                status=HealthStatus.HEALTHY,
                message="Configuration loaded successfully",
                details={"keys": list(data.keys())},
            )
        except Exception as e:
            return HealthCheckResult(
                name="configuration",
                status=HealthStatus.UNHEALTHY,
                message=f"Configuration check failed: {e}",
            )

    def check_write_permissions(self) -> HealthCheckResult:
        try:
            temp_path = Paths.root() / ".write_test"
            temp_path.write_text("test", encoding="utf-8")
            temp_path.unlink()
            return HealthCheckResult(
                name="write_permissions",
                status=HealthStatus.HEALTHY,
                message="Write permissions OK",
            )
        except Exception as e:
            return HealthCheckResult(
                name="write_permissions",
                status=HealthStatus.UNHEALTHY,
                message=f"Write permissions check failed: {e}",
            )

    def check_dataset(self) -> HealthCheckResult:
        dataset_dir = Paths.dataset_dir()
        if not dataset_dir.exists():
            return HealthCheckResult(
                name="dataset",
                status=HealthStatus.DEGRADED,
                message="Dataset directory does not exist",
            )
        try:
            items = list(dataset_dir.iterdir())
            file_count = sum(1 for p in items if p.is_file())
            dir_count = sum(1 for p in items if p.is_dir())
            return HealthCheckResult(
                name="dataset",
                status=HealthStatus.HEALTHY,
                message=f"Dataset directory OK: {file_count} files, {dir_count} subdirectories",
                details={"file_count": file_count, "dir_count": dir_count, "path": str(dataset_dir)},
            )
        except Exception as e:
            return HealthCheckResult(
                name="dataset",
                status=HealthStatus.UNHEALTHY,
                message=f"Dataset check failed: {e}",
            )

    def check_models(self) -> HealthCheckResult:
        models_dir = Paths.models_dir()
        if not models_dir.exists():
            return HealthCheckResult(
                name="models",
                status=HealthStatus.DEGRADED,
                message="Models directory does not exist",
            )
        try:
            model_files = [p for p in models_dir.iterdir() if p.is_file()]
            return HealthCheckResult(
                name="models",
                status=HealthStatus.HEALTHY,
                message=f"Models directory OK: {len(model_files)} files",
                details={"file_count": len(model_files), "path": str(models_dir)},
            )
        except Exception as e:
            return HealthCheckResult(
                name="models",
                status=HealthStatus.UNHEALTHY,
                message=f"Models check failed: {e}",
            )

    def check_cache(self) -> HealthCheckResult:
        cache_dir = Paths.root() / "cache"
        if not cache_dir.exists():
            return HealthCheckResult(
                name="cache",
                status=HealthStatus.DEGRADED,
                message="Cache directory does not exist",
            )
        try:
            file_count = len(list(cache_dir.iterdir()))
            return HealthCheckResult(
                name="cache",
                status=HealthStatus.HEALTHY,
                message=f"Cache OK: {file_count} entries",
                details={"file_count": file_count, "path": str(cache_dir)},
            )
        except Exception as e:
            return HealthCheckResult(
                name="cache",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache check failed: {e}",
            )

    def run_all(self) -> list[HealthCheckResult]:
        return [
            self.check_cuda(),
            self.check_disk(),
            self.check_configuration(),
            self.check_write_permissions(),
            self.check_dataset(),
            self.check_models(),
            self.check_cache(),
        ]

    def run_selected(self, checks: list[str]) -> list[HealthCheckResult]:
        check_map = {
            "cuda": self.check_cuda,
            "disk": self.check_disk,
            "configuration": self.check_configuration,
            "write_permissions": self.check_write_permissions,
            "dataset": self.check_dataset,
            "models": self.check_models,
            "cache": self.check_cache,
        }
        results: list[HealthCheckResult] = []
        for name in checks:
            func = check_map.get(name)
            if func:
                results.append(func())
        return results

    @property
    def is_healthy(self) -> bool:
        return all(r.passed for r in self.run_all())

    @property
    def summary(self) -> dict[str, Any]:
        results = self.run_all()
        return {
            "total": len(results),
            "healthy": sum(1 for r in results if r.passed),
            "degraded": sum(1 for r in results if r.status == HealthStatus.DEGRADED),
            "unhealthy": sum(1 for r in results if r.status == HealthStatus.UNHEALTHY),
            "checks": [r.to_dict() for r in results],
        }
