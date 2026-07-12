import pytest

from src.core.exceptions import (
    BusinessCardAIError,
    ConfigurationError,
    DatasetError,
    FileError,
    InferenceError,
    ModelError,
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

    def test_all_are_business_card_ai_errors(self) -> None:
        errors = [
            ConfigurationError("x"),
            FileError("x"),
            ModelError("x"),
            InferenceError("x"),
            DatasetError("x"),
        ]
        for err in errors:
            assert isinstance(err, BusinessCardAIError)
