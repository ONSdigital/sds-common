"""Tests for SdsSchemaRequestService."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from sds_common.models.schema_publish_errors import SchemaMetadataError, SchemaPostError
from sds_common.schema.schema import Schema


@pytest.fixture
def make_response():
    def _make_response(status_code: int, body=None):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = status_code
        resp.json.return_value = body if body is not None else {}
        return resp

    return _make_response


class TestGetSchemaMetadata:
    def test_returns_list_on_200(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(200, [{"schema_version": "v1"}])
        result = svc.get_metadata("surv1")
        assert result == [{"schema_version": "v1"}]

    def test_returns_none_on_404(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(404)
        assert svc.get_metadata("new_survey") is None

    def test_raises_on_500_and_logs_warning(self, mock_schema_request_service, make_response):
        from unittest.mock import patch
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(500)
        with patch("sds_common.services.sds_schema_request_service.logger") as mock_logger:
            with pytest.raises(SchemaMetadataError):
                svc.get_metadata("surv1")
        mock_logger.warning.assert_called_once()

    def test_calls_correct_url_with_survey_id(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(200, [])
        svc.get_metadata("surv1")
        http.make_get_request.assert_called_once_with(
            "https://sds.test/schemas/metadata", params={"survey_id": "surv1"}
        )


class TestGetAllSchemaMetadata:
    def test_returns_list_on_200(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(200, [{"survey_id": "s1"}])
        result = svc.get_all_metadata()
        assert result == [{"survey_id": "s1"}]

    def test_raises_on_error(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(503, {})
        with pytest.raises(SchemaMetadataError):
            svc.get_all_metadata()

    def test_calls_correct_url(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_get_request.return_value = make_response(200, [])
        svc.get_all_metadata()
        http.make_get_request.assert_called_once_with("https://sds.test/schemas/all-metadata")


class TestPostSchema:
    def test_post_schema_200_returns_response(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_post_request.return_value = make_response(200)
        schema = Schema({"data": 1}, "surv1", "v1", "v1.json")
        resp = svc.publish(schema)
        assert resp.status_code == 200

    def test_post_schema_calls_correct_url(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_post_request.return_value = make_response(200)
        schema = Schema({"data": 1}, "surv1", "v1", "v1.json")
        svc.publish(schema)
        http.make_post_request.assert_called_once_with(
            "https://sds.test/schemas", {"data": 1}, params={"survey_id": "surv1"}
        )

    def test_post_schema_raises_on_non_200(self, mock_schema_request_service, make_response):
        svc, http = mock_schema_request_service
        http.make_post_request.return_value = make_response(400)
        schema = Schema({"data": 1}, "surv1", "v1", "v1.json")
        with pytest.raises(SchemaPostError):
            svc.publish(schema)
