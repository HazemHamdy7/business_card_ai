class BusinessCardAIError(Exception):
    """Base exception for all Business Card AI errors."""


class ConfigurationError(BusinessCardAIError):
    """Raised when configuration loading or validation fails."""


class ValidationError(ConfigurationError):
    """Raised when configuration validation fails."""


class FileError(BusinessCardAIError):
    """Raised when file operations fail."""


class ModelError(BusinessCardAIError):
    """Raised when model loading or inference fails."""


class InferenceError(BusinessCardAIError):
    """Raised when inference operations fail."""


class DatasetError(BusinessCardAIError):
    """Raised when dataset operations fail."""


class CircularDependencyError(BusinessCardAIError):
    """Raised when a circular dependency is detected."""


class ServiceNotFoundError(BusinessCardAIError):
    """Raised when a service is not found in the registry."""


class RegistrationError(BusinessCardAIError):
    """Raised when service registration fails."""


class HealthCheckError(BusinessCardAIError):
    """Raised when a health check fails."""


class ResourceExhaustedError(BusinessCardAIError):
    """Raised when a resource is exhausted."""
