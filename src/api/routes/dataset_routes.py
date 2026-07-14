from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..config import APIConfig
from ..dependencies import get_config
from ..response_models import DatasetInfoResponse

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.get("/status", response_model=DatasetInfoResponse)
async def dataset_status(
    dataset_root: Optional[str] = None,
    config: APIConfig = Depends(get_config),
) -> DatasetInfoResponse:
    root = dataset_root or os.getenv("DATASET_ROOT", "dataset")
    if not os.path.isdir(root):
        return DatasetInfoResponse(ready=False)

    try:
        from src.dataset.dataset_quality import DatasetQuality
        from src.dataset.dataset_balance import DatasetBalance

        quality = DatasetQuality()
        quality_result = quality.evaluate(image_dir=root)

        balance = DatasetBalance()
        balance_result = balance.analyze()

        return DatasetInfoResponse(
            ready=quality_result.overall_score >= 70.0,
            quality_score=round(quality_result.overall_score, 1),
            total_images=quality_result.total_images,
            total_labels=quality_result.total_labels,
            num_classes=balance_result.num_classes,
            total_objects=balance_result.total_objects,
            imbalance_score=round(balance_result.imbalance_score, 2),
        )
    except ImportError:
        return DatasetInfoResponse(
            ready=False,
            message="Dataset modules not available",
        )
    except Exception:
        return DatasetInfoResponse(ready=False)
