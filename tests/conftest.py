"""Shared pytest fixtures."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from sds_common.config.config import Config, get_config
from sds_common.schema.schema import Schema


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Ensure the get_config lru_cache is reset between tests so env patches don't bleed across."""
    get_config.cache_clear()
    yield
    get_config.cache_clear()


@pytest.fixture
def base_config() -> Config:
    with patch.dict(
        "os.environ",
        {
            "PROJECT_ID": "test-project",
            "SDS_URL": "https://sds.test",
            "SDS_LOADER_URL": "https://loader.test",
            "HTTP_REQUEST_TIMEOUT_SECONDS": "60",
            "IAP_SECRET_ID": "test-secret",
            "FIRESTORE_DB_NAME": "test-project-sds",
            "SCHEMA_STAGING_BUCKET_NAME": "test-project-schema-publish",
            "DATASET_BUCKET_NAME": "test-project-dataset",
        },
        clear=False,
    ):
        yield Config()


@pytest.fixture
def valid_schema_json() -> dict:
    return {
        "properties": {
            "survey_id": {"enum": ["abc123"]},
            "schema_version": {"const": "v1"},
        }
    }


@pytest.fixture
def valid_schema(valid_schema_json) -> Schema:
    return Schema(valid_schema_json, "abc123", "v1", "v1.json")
