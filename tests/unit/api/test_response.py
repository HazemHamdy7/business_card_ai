import pytest
from fastapi.responses import JSONResponse

from src.api.response import success_response, error_response


class TestSuccessResponse:
    def test_success_response_defaults(self):
        response = success_response()
        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        data = response.body.decode()
        assert '"success"' in data
        assert '"message"' in data

    def test_success_response_with_data(self):
        response = success_response(data={"key": "value"})
        data = response.body.decode()
        assert '"key"' in data
        assert '"value"' in data

    def test_success_response_custom_code(self):
        response = success_response(status_code=201)
        assert response.status_code == 201

    def test_success_response_custom_message(self):
        response = success_response(message="Created", status_code=201)
        data = response.body.decode()
        assert '"Created"' in data


class TestErrorResponse:
    def test_error_response_defaults(self):
        response = error_response("An error occurred")
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        data = response.body.decode()
        assert '"success"' in data
        assert '"error"' not in data

    def test_error_response_custom_code(self):
        response = error_response("Not found", status_code=404)
        assert response.status_code == 404

    def test_error_response_with_details(self):
        response = error_response("Validation failed", details={"field": "required"})
        data = response.body.decode()
        assert '"details"' in data
