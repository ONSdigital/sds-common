"""Tests for GcsSchemaPublisher."""
from __future__ import annotations

from unittest.mock import MagicMock

import requests

from sds_common.publishers.gcs_schema_publisher import GcsSchemaPublisher


VALID_SCHEMA_JSON = {
    "properties": {
        "survey_id": {"enum": ["surv1"]},
        "schema_version": {"const": "v1"},
    }
}


def _make_publisher():
    schema_req_svc = MagicMock()
    file_service = MagicMock()
    file_service.get_json.return_value = VALID_SCHEMA_JSON
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    schema_req_svc.publish.return_value = resp
    return GcsSchemaPublisher(
        schema_request_service=schema_req_svc,
        file_service=file_service,
    ), schema_req_svc, file_service


class TestGcsSchemaPublisher:
    def test_publish_schema_retrieves_and_posts(self):
        pub, schema_svc, file_svc = _make_publisher()
        pub.publish("v1.json")
        file_svc.get_json.assert_called_once_with("v1.json")
        schema_svc.publish.assert_called_once()

    def test_publish_schema_returns_response(self):
        pub, schema_svc, file_svc = _make_publisher()
        resp = pub.publish("v1.json")
        assert resp.status_code == 200

    def test_cleanup_deletes_file(self):
        pub, _, file_svc = _make_publisher()
        pub.cleanup("v1.json")
        file_svc.delete.assert_called_once_with("v1.json")

    def test_retrieve_schema_calls_file_service(self):
        pub, _, file_svc = _make_publisher()
        result = pub._retrieve_schema("v1.json")
        assert result is VALID_SCHEMA_JSON
