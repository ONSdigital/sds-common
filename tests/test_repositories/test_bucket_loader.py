"""Tests for BucketLoader."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from google.cloud import exceptions

from sds_common.enums.buckets import Bucket
from sds_common.repositories.bucket_loader import BucketLoader


def _make_loader(config=None):
    storage_client = MagicMock()
    cfg = config or MagicMock()
    cfg.SCHEMA_PUBLISH_BUCKET_NAME = "proj-schema-publish"
    cfg.SCHEMA_PUBLISH_BUCKET_NAME = "proj-schema-publish"
    cfg.DATASET_BUCKET_NAME = "proj-dataset"
    return BucketLoader(storage_client=storage_client, config=cfg), storage_client


class TestBucketLoader:
    def test_fetch_bucket_returns_bucket(self):
        loader, client = _make_loader()
        mock_bucket = MagicMock()
        client.get_bucket.return_value = mock_bucket
        result = loader.fetch_bucket(Bucket.SCHEMA_PUBLISH_BUCKET)
        assert result is mock_bucket
        client.get_bucket.assert_called_once_with("proj-schema-publish")

    def test_fetch_bucket_caches_result(self):
        loader, client = _make_loader()
        mock_bucket = MagicMock()
        client.get_bucket.return_value = mock_bucket
        r1 = loader.fetch_bucket(Bucket.SCHEMA_PUBLISH_BUCKET)
        r2 = loader.fetch_bucket(Bucket.SCHEMA_PUBLISH_BUCKET)
        assert r1 is r2
        assert client.get_bucket.call_count == 1

    def test_fetch_bucket_raises_on_not_found(self):
        from unittest.mock import patch
        from sds_common.models.storage_errors import BucketNotFoundError
        loader, client = _make_loader()
        client.get_bucket.side_effect = exceptions.NotFound("not found")
        with patch("sds_common.repositories.bucket_loader.logger") as mock_logger:
            with pytest.raises(BucketNotFoundError) as exc_info:
                loader.fetch_bucket(Bucket.SCHEMA_PUBLISH_BUCKET)
        assert "proj-schema-publish" in str(exc_info.value)
        mock_logger.warning.assert_called_once()  # error is logged before raising
        assert isinstance(exc_info.value.__cause__, exceptions.NotFound)

    def test_fetch_bucket_raises_on_wrong_type(self):
        loader, _ = _make_loader()
        with pytest.raises(TypeError):
            loader.fetch_bucket("not-an-enum")

    def test_resolve_bucket_name_schema(self):
        loader, _ = _make_loader()
        assert loader.resolve_bucket_name(Bucket.SCHEMA_PUBLISH_BUCKET) == "proj-schema-publish"

    def test_resolve_bucket_name_dataset(self):
        loader, _ = _make_loader()
        assert loader.resolve_bucket_name(Bucket.DATASET_BUCKET) == "proj-dataset"

    def test_resolve_bucket_name_schema_publish(self):
        loader, _ = _make_loader()
        assert loader.resolve_bucket_name(Bucket.SCHEMA_PUBLISH_BUCKET) == "proj-schema-publish"

    def test_each_bucket_enum_maps_correctly(self):
        loader, client = _make_loader()
        for bucket in Bucket:
            client.get_bucket.return_value = MagicMock()
            loader._bucket_cache.clear()
            loader.fetch_bucket(bucket)
            client.get_bucket.assert_called()
