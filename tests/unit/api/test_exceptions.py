import pytest

from src.api.exceptions import (
    BusinessCardAIException,
    ResourceNotFoundException,
    ValidationError,
    ConfigurationError,
)


class TestBusinessCardAIException:
    def test_base_exception(self):
        exc = BusinessCardAIException("test error", 400)
        assert exc.message == "test error"
        assert exc.status_code == 400
        assert exc.details == {}

    def test_base_exception_with_details(self):
        exc = BusinessCardAIException("test error", 400, {"field": "value"})
        assert exc.details == {"field": "value"}

    def test_default_status_code(self):
        exc = BusinessCardAIException("error")
        assert exc.status_code == 500


class TestResourceNotFoundException:
    def test_default(self):
        exc = ResourceNotFoundException()
        assert exc.status_code == 404
        assert exc.message == "Resource not found"

    def test_custom_resource(self):
        exc = ResourceNotFoundException("Dataset")
        assert exc.message == "Dataset not found"


class TestValidationError:
    def test_default_status(self):
        exc = ValidationError("Invalid input")
        assert exc.status_code == 422
        assert exc.message == "Invalid input"

    def test_inheritance(self):
        exc = ValidationError("bad")
        assert isinstance(exc, BusinessCardAIException)


class TestConfigurationError:
    def test_default_status(self):
        exc = ConfigurationError("Bad config")
        assert exc.status_code == 500
        assert exc.message == "Bad config"

    def test_inheritance(self):
        exc = ConfigurationError("Bad config")
        assert isinstance(exc, BusinessCardAIException)
