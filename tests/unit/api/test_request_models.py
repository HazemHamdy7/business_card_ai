import pytest
from pydantic import ValidationError as PydanticValidationError

from src.api.request_models import HealthRequest, PredictionRequest, DatasetQuery


class TestHealthRequest:
    def test_defaults(self):
        req = HealthRequest()
        assert req.detailed is False

    def test_custom_values(self):
        req = HealthRequest(detailed=True)
        assert req.detailed is True


class TestPredictionRequest:
    def test_required_fields(self):
        with pytest.raises(PydanticValidationError):
            PredictionRequest()

    def test_valid_request(self):
        req = PredictionRequest(image="base64encodedstring")
        assert req.image == "base64encodedstring"
        assert req.options is None

    def test_with_options(self):
        req = PredictionRequest(image="img", options={"model": "v1"})
        assert req.options["model"] == "v1"


class TestDatasetQuery:
    def test_defaults(self):
        req = DatasetQuery()
        assert req.dataset_root == "dataset"

    def test_custom_values(self):
        req = DatasetQuery(dataset_root="/data")
        assert req.dataset_root == "/data"
