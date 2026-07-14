from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    body: Dict[str, Any] = {
        "success": True,
        "message": message,
    }
    if data is not None:
        body["data"] = data
    return JSONResponse(content=body, status_code=status_code)


def error_response(
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    body: Dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if details:
        body["details"] = details
    return JSONResponse(content=body, status_code=status_code)
