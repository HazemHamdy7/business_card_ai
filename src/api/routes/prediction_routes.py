from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..request_models import PredictionRequest
from ..response_models import PredictionResponse

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(_body: PredictionRequest) -> PredictionResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Prediction pipeline is not implemented yet.",
    )


@router.post(
    "/detect",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def detect() -> dict:
    return {
        "success": False,
        "message": "Object detection pipeline is not implemented yet.",
    }


@router.post(
    "/ocr",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def ocr() -> dict:
    return {
        "success": False,
        "message": "OCR pipeline is not implemented yet.",
    }


@router.post(
    "/business-card",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def business_card() -> dict:
    return {
        "success": False,
        "message": "Business card processing pipeline is not implemented yet.",
    }
