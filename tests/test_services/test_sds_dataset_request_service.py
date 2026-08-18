"""Tests for SdsDatasetRequestService."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from sds_common.models.dataset_publish_errors import DatasetMetadataRetrievalError
from sds_common.services.sds_dataset_request_service import SdsDatasetRequestService


def _make_response(status_code: int, body=None):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = body or []
    return resp


def _make_service():
    http = MagicMock()
    cfg = MagicMock()
    cfg.SDS_URL = "https://sds.test"
    cfg.GET_DATASET_METADATA_ENDPOINT = "/datasets/metadata"
    return SdsDatasetRequestService(http_service=http, config=cfg), http


class TestSdsDatasetRequestService:
    def test_get_metadata_200(self):
        svc, http = _make_service()
        body = [
            {
                "dataset_id": "d1",
                "survey_id": "s1",
                "period_id": "p1",
                "form_types": ["f1"],
                "sds_published_at": "2024-01-01",
                "total_reporting_units": 5,
                "sds_dataset_version": 1,
                "filename": "file.json",
            }
        ]
        http.make_get_request.return_value = _make_response(200, body)
        result = svc.get_metadata("s1", "p1")
        assert len(result) == 1
        assert result[0].dataset_id == "d1"
        http.make_get_request.assert_called_once_with(
            "https://sds.test/datasets/metadata",
            params={"survey_id": "s1", "period_id": "p1"},
        )

    def test_get_metadata_returns_none_on_404(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(404)
        result = svc.get_metadata("s1", "p1")
        assert result is None

    def test_get_metadata_raises_on_non_200(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(500)
        with patch("sds_common.services.sds_dataset_request_service.logger") as mock_logger:
            with pytest.raises(DatasetMetadataRetrievalError):
                svc.get_metadata("s1", "p1")
        mock_logger.warning.assert_called_once()

    def test_get_metadata_returns_empty_list(self):
        svc, http = _make_service()
        http.make_get_request.return_value = _make_response(200, [])
        result = svc.get_metadata("s1", "p1")
        assert result == []
