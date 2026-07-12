class BusinessCardAIError(Exception):
    """Base exception for all Business Card AI errors."""


class ConfigurationError(BusinessCardAIError):
    """Raised when configuration loading or validation fails."""


class FileError(BusinessCardAIError):
    """Raised when file operations fail."""


class ModelError(BusinessCardAIError):
    """Raised when model loading or inference fails."""


class InferenceError(BusinessCardAIError):
    """Raised when inference operations fail."""


class DatasetError(BusinessCardAIError):
    """Raised when dataset operations fail."""
