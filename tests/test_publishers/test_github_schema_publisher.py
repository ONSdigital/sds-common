"""Tests for GithubSchemaPublisher."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from sds_common.models.schema_publish_errors import SchemaFetchError, SchemaDuplicationError
from sds_common.publishers.github_schema_publisher import GithubSchemaPublisher


VALID_SCHEMA_JSON = {
    "properties": {
        "survey_id": {"enum": ["surv1"]},
        "schema_version": {"const": "v1"},
    }
}


def _make_publisher(schema_json=None, fetch_raises=False, validate_raises=None):
    schema_req_svc = MagicMock()
    validator_svc = MagicMock()
    http_svc = MagicMock()

    response = MagicMock(spec=requests.Response)
    response.status_code = 200 if not fetch_raises else 404
    response.json.return_value = schema_json or VALID_SCHEMA_JSON
    http_svc.make_get_request.return_value = response

    post_resp = MagicMock(spec=requests.Response)
    post_resp.status_code = 200
    schema_req_svc.publish.return_value = post_resp

    if validate_raises:
        validator_svc.validate.side_effect = validate_raises

    pub = GithubSchemaPublisher(
        schema_request_service=schema_req_svc,
        validator_service=validator_svc,
        github_schema_url="https://github.com/schemas/",
        http_service=http_svc,
    )
    return pub, schema_req_svc, validator_svc, http_svc


class TestGithubSchemaPublisher:
    def test_publish_schema_retrieves_validates_and_posts(self):
        pub, schema_svc, validator_svc, http_svc = _make_publisher()
        pub.publish("v1.json")
        http_svc.make_get_request.assert_called_once_with("https://github.com/schemas/v1.json")
        validator_svc.validate.assert_called_once()
        schema_svc.publish.assert_called_once()

    def test_publish_schema_raises_fetch_error_on_non_200(self):
        pub, _, _, _ = _make_publisher(fetch_raises=True)
        with pytest.raises(SchemaFetchError):
            pub.publish("v1.json")

    def test_publish_schema_propagates_validation_error(self):
        pub, _, _, _ = _make_publisher(validate_raises=SchemaDuplicationError("v1.json"))
        with pytest.raises(SchemaDuplicationError):
            pub.publish("v1.json")

    def test_retrieve_schema_fetches_from_github_url(self):
        pub, _, _, http_svc = _make_publisher()
        result = pub._retrieve_schema("v1.json")
        assert result == VALID_SCHEMA_JSON
        http_svc.make_get_request.assert_called_once_with("https://github.com/schemas/v1.json")

    def test_validate_calls_validator_service(self):
        pub, _, validator_svc, _ = _make_publisher()
        from sds_common.schema.schema import Schema
        schema = Schema(VALID_SCHEMA_JSON, "surv1", "v1", "v1.json")
        pub._validate(schema)
        validator_svc.validate.assert_called_once_with(schema)
