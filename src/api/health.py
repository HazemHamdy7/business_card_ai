from __future__ import annotations

import os
import platform
import sys
import time
from typing import Any, Dict, Optional

from .config import APIConfig
from .version import VERSION


_start_time: float = time.time()


def _get_memory_usage() -> Optional[Dict[str, Any]]:
    try:
        import psutil
        process = psutil.Process()
        mem = process.memory_info()
        return {
            "rss_bytes": mem.rss,
            "vms_bytes": mem.vms,
            "rss_mb": round(mem.rss / 1024 / 1024, 2),
            "vms_mb": round(mem.vms / 1024 / 1024, 2),
        }
    except ImportError:
        return None


def _get_disk_usage() -> Optional[Dict[str, Any]]:
    try:
        import psutil
        usage = psutil.disk_usage(os.getcwd())
        return {
            "total_gb": round(usage.total / 1024**3, 2),
            "used_gb": round(usage.used / 1024**3, 2),
            "free_gb": round(usage.free / 1024**3, 2),
            "percent_used": usage.percent,
        }
    except ImportError:
        return None


def _get_gpu_info() -> Dict[str, bool]:
    cuda_available = False
    gpu_available = False
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        gpu_available = cuda_available or torch.backends.mps.is_available()
    except ImportError:
        pass
    return {
        "gpu_available": gpu_available,
        "cuda_available": cuda_available,
    }


def get_health_info(config: APIConfig) -> Dict[str, Any]:
    gpu_info = _get_gpu_info()
    return {
        "status": "healthy",
        "version": VERSION,
        "python_version": sys.version,
        "gpu_available": gpu_info["gpu_available"],
        "cuda_available": gpu_info["cuda_available"],
        "memory_usage": _get_memory_usage(),
        "disk_usage": _get_disk_usage(),
        "uptime_seconds": round(time.time() - _start_time, 2),
        "environment": config.env.value,
    }


def get_system_info() -> Dict[str, Any]:
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count() or 0,
        "memory": _get_memory_usage(),
        "environment": os.getenv("APP_ENV", "development"),
    }
