from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..response_models import AnnotationResponse

router = APIRouter(prefix="/annotation", tags=["Annotation"])


@router.get("/status", response_model=AnnotationResponse)
async def annotation_status(
    label_dir: Optional[str] = None,
) -> AnnotationResponse:
    lbl_dir = label_dir or os.getenv("LABEL_DIR", "dataset/train/labels")
    if not os.path.isdir(lbl_dir):
        return AnnotationResponse(ready=False)

    try:
        from src.annotations import AnnotationManager

        manager = AnnotationManager()
        report = manager.run(label_dir=lbl_dir)

        return AnnotationResponse(
            ready=report.total_invalid_files == 0,
            total_files=report.total_valid_files + report.total_invalid_files,
            total_objects=report.total_objects,
            valid_files=report.total_valid_files,
            invalid_files=report.total_invalid_files,
        )
    except ImportError:
        return AnnotationResponse(
            ready=False,
            message="Annotation modules not available",
        )
    except Exception:
        return AnnotationResponse(ready=False)
