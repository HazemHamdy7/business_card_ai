from src.api.response_models import (
    ErrorResponse,
    HealthResponse,
    PredictionResponse,
    DatasetInfoResponse,
    AnnotationResponse,
    SystemInfoResponse,
    APIInfoResponse,
)


class TestErrorResponse:
    def test_defaults(self):
        resp = ErrorResponse()
        assert resp.success is False
        assert resp.status_code == 500
        assert resp.details is None

    def test_custom(self):
        resp = ErrorResponse(message="error", status_code=400, details={"field": "bad"})
        assert resp.details["field"] == "bad"

    def test_timestamp_generated(self):
        resp = ErrorResponse(message="msg", status_code=500)
        assert resp.timestamp is not None


class TestHealthResponse:
    def test_defaults(self):
        resp = HealthResponse()
        assert resp.status == "healthy"
        assert resp.version == "0.1.0"

    def test_full(self):
        resp = HealthResponse(
            status="healthy",
            version="1.0",
            python_version="3.11",
            gpu_available=True,
            cuda_available=False,
        )
        assert resp.gpu_available is True
        assert resp.cuda_available is False


class TestPredictionResponse:
    def test_defaults(self):
        resp = PredictionResponse()
        assert resp.success is True
        assert resp.predictions is None

    def test_custom(self):
        resp = PredictionResponse(
            success=False,
            message="Not implemented",
            predictions=[],
        )
        assert not resp.success
        assert len(resp.predictions) == 0


class TestDatasetInfoResponse:
    def test_defaults(self):
        resp = DatasetInfoResponse()
        assert not resp.ready
        assert resp.total_images == 0

    def test_full(self):
        resp = DatasetInfoResponse(
            ready=True,
            quality_score=85.5,
            total_images=100,
            total_labels=3,
            num_classes=5,
            total_objects=200,
            imbalance_score=0.3,
        )
        assert resp.ready
        assert resp.quality_score == 85.5
        assert resp.num_classes == 5


class TestAnnotationResponse:
    def test_defaults(self):
        resp = AnnotationResponse()
        assert not resp.ready

    def test_full(self):
        resp = AnnotationResponse(
            ready=True,
            total_files=50,
            total_objects=150,
            valid_files=48,
            invalid_files=2,
        )
        assert resp.ready
        assert resp.invalid_files == 2


class TestSystemInfoResponse:
    def test_required_only(self):
        resp = SystemInfoResponse(
            python_version="3.11",
            platform="Windows",
            cpu_count=8,
            environment="development",
        )
        assert resp.python_version == "3.11"
        assert resp.cpu_count == 8

    def test_defaults(self):
        resp = SystemInfoResponse()
        assert resp.python_version == ""
        assert resp.cpu_count == 0


class TestAPIInfoResponse:
    def test_full(self):
        resp = APIInfoResponse(
            title="API",
            version="1.0",
            api_version="v1",
            description="desc",
            status="running",
        )
        assert resp.title == "API"
        assert resp.status == "running"

    def test_defaults(self):
        resp = APIInfoResponse()
        assert resp.title == "Business Card AI API"
