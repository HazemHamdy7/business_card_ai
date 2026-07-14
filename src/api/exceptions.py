from __future__ import annotations

from typing import Any, Dict, Optional


class BusinessCardAIException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundException(BusinessCardAIException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
        )


class ValidationError(BusinessCardAIException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)


class ConfigurationError(BusinessCardAIException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)
