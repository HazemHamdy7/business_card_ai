import pytest

from src.core.exceptions import (
    BusinessCardAIError,
    CircularDependencyError,
    ConfigurationError,
    DatasetError,
    FileError,
    HealthCheckError,
    InferenceError,
    ModelError,
    RegistrationError,
    ResourceExhaustedError,
    ServiceNotFoundError,
)


class TestExceptions:
    def test_base_exception(self) -> None:
        with pytest.raises(BusinessCardAIError):
            raise BusinessCardAIError("base error")

    def test_configuration_error(self) -> None:
        with pytest.raises(ConfigurationError) as exc:
            raise ConfigurationError("config error")
        assert str(exc.value) == "config error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_file_error(self) -> None:
        with pytest.raises(FileError) as exc:
            raise FileError("file error")
        assert str(exc.value) == "file error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_model_error(self) -> None:
        with pytest.raises(ModelError) as exc:
            raise ModelError("model error")
        assert str(exc.value) == "model error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_inference_error(self) -> None:
        with pytest.raises(InferenceError) as exc:
            raise InferenceError("inference error")
        assert str(exc.value) == "inference error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_dataset_error(self) -> None:
        with pytest.raises(DatasetError) as exc:
            raise DatasetError("dataset error")
        assert str(exc.value) == "dataset error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_circular_dependency_error(self) -> None:
        with pytest.raises(CircularDependencyError) as exc:
            raise CircularDependencyError("circular dep")
        assert str(exc.value) == "circular dep"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_service_not_found_error(self) -> None:
        with pytest.raises(ServiceNotFoundError) as exc:
            raise ServiceNotFoundError("not found")
        assert str(exc.value) == "not found"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_registration_error(self) -> None:
        with pytest.raises(RegistrationError) as exc:
            raise RegistrationError("reg error")
        assert str(exc.value) == "reg error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_health_check_error(self) -> None:
        with pytest.raises(HealthCheckError) as exc:
            raise HealthCheckError("health error")
        assert str(exc.value) == "health error"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_resource_exhausted_error(self) -> None:
        with pytest.raises(ResourceExhaustedError) as exc:
            raise ResourceExhaustedError("resource exhausted")
        assert str(exc.value) == "resource exhausted"
        assert isinstance(exc.value, BusinessCardAIError)

    def test_all_are_business_card_ai_errors(self) -> None:
        errors = [
            ConfigurationError("x"),
            FileError("x"),
            ModelError("x"),
            InferenceError("x"),
            DatasetError("x"),
            CircularDependencyError("x"),
            ServiceNotFoundError("x"),
            RegistrationError("x"),
            HealthCheckError("x"),
            ResourceExhaustedError("x"),
        ]
        for err in errors:
            assert isinstance(err, BusinessCardAIError)
