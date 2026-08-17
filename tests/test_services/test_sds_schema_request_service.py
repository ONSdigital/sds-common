"""Tests for SdsSchemaRequestService."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from sds_common.models.schema_publish_errors import SchemaMetadataError, SchemaPostError
from sds_common.schema.schema import Schema
from sds_common.services.sds_schema_request_service import SdsSchemaRequestService


def _make_response(status_code: int, body=None):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = body if body is not None else {}
    return resp


def _make_service(config=None):
    http = MagicMock()
    cfg = config or MagicMock()
    cfg.SDS_URL = "https://sds.test"
    cfg.GET_SCHEMA_METADATA_ENDPOINT = "/v1/schema_metadata"
    cfg.GET_ALL_SCHEMA_METADATA_ENDPOINT = "/v1/all_schema_metadata"
    cfg.POST_SCHEMA_ENDPOINT = "/v1/schema"
    return SdsSchemaRequestService(http_service=http, config=cfg), http


class TestGetSchemaMetadata:
    def test_returns_list_on_200(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(200, [{"schema_version": "v1"}])
        result = svc.get_schema_metadata("surv1")
        assert result == [{"schema_version": "v1"}]

    def test_returns_none_on_404(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(404)
        assert svc.get_schema_metadata("new_survey") is None

    def test_raises_on_500_and_logs_warning(self):
        from unittest.mock import patch
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(500)
        with patch("sds_common.services.sds_schema_request_service.logger") as mock_logger:
            with pytest.raises(SchemaMetadataError):
                svc.get_schema_metadata("surv1")
        mock_logger.warning.assert_called_once()

    def test_calls_correct_url_with_survey_id(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(200, [])
        svc.get_schema_metadata("surv1")
        http.make_get_request.assert_called_once_with(
            "https://sds.test/v1/schema_metadata", params={"survey_id": "surv1"}
        )


class TestGetAllSchemaMetadata:
    def test_returns_list_on_200(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(200, [{"survey_id": "s1"}])
        result = svc.get_all_schema_metadata()
        assert result == [{"survey_id": "s1"}]

    def test_raises_on_error(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(503, {})
        with pytest.raises(SchemaMetadataError):
            svc.get_all_schema_metadata()

    def test_calls_correct_url(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(200, [])
        svc.get_all_schema_metadata()
        http.make_get_request.assert_called_once_with("https://sds.test/v1/all_schema_metadata")


class TestPostSchema:
    def test_post_schema_200_returns_response(self):
        svc, http = _make_service()
        http.make_post_request.return_value = _make_response(200)
        schema = Schema({"data": 1}, "surv1", "v1", "v1.json")
        resp = svc.post_schema(schema)
        assert resp.status_code == 200

    def test_post_schema_calls_correct_url(self):
        svc, http = _make_service()
        http.make_post_request.return_value = _make_response(200)
        schema = Schema({"data": 1}, "surv1", "v1", "v1.json")
        svc.post_schema(schema)
        http.make_post_request.assert_called_once_with(
            "https://sds.test/v1/schema", {"data": 1}, params={"survey_id": "surv1"}
        )

    def test_post_schema_raises_on_non_200(self):
        svc, http = _make_service()
        http.make_post_request.return_value = _make_response(400)
        schema = Schema({"data": 1}, "surv1", "v1", "v1.json")
        with pytest.raises(SchemaPostError):
            svc.post_schema(schema)
