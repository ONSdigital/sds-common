"""Tests for the SdsCommon facade."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from sds_common.enums.buckets import Bucket
from sds_common.sds_common import SdsCommon
from sds_common.services.auth_header_provider import AuthHeaderProvider
from sds_common.services.secret_service import SecretService


class TestSdsCommonLaziness:
    """Verify no GCP clients are instantiated at construction time."""

    def test_instantiation_does_not_raise(self, base_config):
        client = SdsCommon(config=base_config)
        assert client is not None

    def test_config_property_returns_injected_config(self, base_config):
        client = SdsCommon(config=base_config)
        assert client.config is base_config

    def test_config_property_returns_default_config_when_none_given(self):
        client = SdsCommon()
        assert client.config.PROJECT_ID is not None

    def test_secret_service_is_lazily_created(self, base_config):
        client = SdsCommon(config=base_config)
        with patch.object(SecretService, "_create_client", return_value=MagicMock()):
            svc = client.secret_service
        assert svc is not None
        assert client.secret_service is svc

    def test_auth_header_provider_is_lazily_created(self, base_config):
        client = SdsCommon(config=base_config)
        with patch.object(SecretService, "_create_client", return_value=MagicMock()):
            provider = client.auth_header_provider
        assert isinstance(provider, AuthHeaderProvider)
        assert client.auth_header_provider is provider

    def test_auth_header_provider_shares_secret_service(self, base_config):
        client = SdsCommon(config=base_config)
        with patch.object(SecretService, "_create_client", return_value=MagicMock()):
            provider = client.auth_header_provider
            secret_svc = client.secret_service
        assert provider.secret_service is secret_svc

    def test_http_service_has_no_headers(self, base_config):
        """Unauthenticated http_service has no headers (for GitHub etc.)."""
        client = SdsCommon(config=base_config)
        svc = client.http_service
        assert svc.headers is None
        assert client.http_service is svc

    def test_bucket_loader_is_lazily_created(self, base_config):
        client = SdsCommon(config=base_config)
        with patch("sds_common.sds_common.storage") as mock_storage:
            mock_storage.Client.return_value = MagicMock()
            loader = client.bucket_loader
        assert loader is not None
        assert client.bucket_loader is loader

    def test_pub_sub_service_is_lazily_created(self, base_config):
        client = SdsCommon(config=base_config)
        with patch("sds_common.sds_common.PublisherClient", return_value=MagicMock()):
            svc = client.pub_sub_service
        assert svc is not None
        assert svc.project_id == "test-project"

    def test_firebase_loader_is_lazily_created(self, base_config):
        client = SdsCommon(config=base_config)
        with patch("sds_common.sds_common.firestore") as mock_fs:
            mock_fs.Client.return_value = MagicMock()
            loader = client.firebase_loader
        assert loader is not None
        assert client.firebase_loader is loader

    def test_firestore_client_is_lazily_created(self, base_config):
        client = SdsCommon(config=base_config)
        with patch("sds_common.sds_common.firestore") as mock_fs:
            mock_fs.Client.return_value = MagicMock()
            fc = client.firestore_client
        assert fc is not None


class TestSdsCommonAuthenticatedHttpService:
    """authenticated_http_service is a plain @property — fresh token every access."""

    def test_authenticated_http_service_has_headers(self, base_config):
        client = SdsCommon(config=base_config)
        mock_provider = MagicMock(spec=AuthHeaderProvider)
        mock_provider.generate.return_value = {"Authorization": "Bearer tok", "Content-Type": "application/json"}
        client.__dict__["auth_header_provider"] = mock_provider

        svc = client.authenticated_http_service

        mock_provider.generate.assert_called_once()
        assert svc.headers == {"Authorization": "Bearer tok", "Content-Type": "application/json"}

    def test_authenticated_http_service_generates_fresh_token_each_access(self, base_config):
        """Property — not cached — so token is re-generated on every access."""
        client = SdsCommon(config=base_config)
        mock_provider = MagicMock(spec=AuthHeaderProvider)
        mock_provider.generate.return_value = {"Authorization": "Bearer tok", "Content-Type": "application/json"}
        client.__dict__["auth_header_provider"] = mock_provider

        client.authenticated_http_service
        client.authenticated_http_service

        assert mock_provider.generate.call_count == 2


class TestSdsCommonDependencyWiring:
    """Verify wiring of injected dependencies within the facade."""

    def test_schema_validator_service_uses_sds_schema_request_service(self, base_config):
        client = SdsCommon(config=base_config)
        mock_req_svc = MagicMock()
        client.__dict__["sds_schema_request_service"] = mock_req_svc
        svc = client.schema_validator_service
        assert svc.sds_schema_request_service is mock_req_svc

    def test_gcs_schema_publisher_wired_correctly(self, base_config):
        client = SdsCommon(config=base_config)
        client.__dict__["sds_schema_request_service"] = MagicMock()
        client.__dict__["schema_publish_file_service"] = MagicMock()
        pub = client.gcs_schema_publisher
        assert pub.schema_request_service is client.sds_schema_request_service
        assert pub.bucket_service is client.schema_publish_file_service

    def test_github_schema_publisher_uses_correct_github_url(self, base_config):
        client = SdsCommon(config=base_config)
        client.__dict__["sds_schema_request_service"] = MagicMock()
        client.__dict__["schema_validator_service"] = MagicMock()
        client.__dict__["http_service"] = MagicMock()
        pub = client.github_schema_publisher
        assert pub.github_schema_url == base_config.GITHUB_SCHEMA_URL

    def test_sds_schema_request_service_uses_authenticated_http(self, base_config):
        client = SdsCommon(config=base_config)
        mock_http = MagicMock()
        mock_provider = MagicMock(spec=AuthHeaderProvider)
        mock_provider.generate.return_value = {"Authorization": "Bearer tok"}
        client.__dict__["auth_header_provider"] = mock_provider
        client.__dict__["_authenticated_session"] = MagicMock()
        svc = client.sds_schema_request_service
        assert svc.http_service.headers == {"Authorization": "Bearer tok"}

    def test_sds_dataset_request_service_uses_authenticated_http(self, base_config):
        client = SdsCommon(config=base_config)
        mock_provider = MagicMock(spec=AuthHeaderProvider)
        mock_provider.generate.return_value = {"Authorization": "Bearer tok"}
        client.__dict__["auth_header_provider"] = mock_provider
        client.__dict__["_authenticated_session"] = MagicMock()
        svc = client.sds_dataset_request_service
        assert svc.http_service.headers == {"Authorization": "Bearer tok"}


class TestSdsCommonFileServices:
    """Cover file-service lazy properties."""

    def _client_with_mock_loader(self, base_config):
        client = SdsCommon(config=base_config)
        mock_loader = MagicMock()
        mock_loader.fetch_bucket.return_value = MagicMock()
        client.__dict__["bucket_loader"] = mock_loader
        return client

    def test_schema_file_service_is_lazily_created(self, base_config):
        client = self._client_with_mock_loader(base_config)
        svc = client.schema_file_service
        assert svc is not None
        assert client.schema_file_service is svc

    def test_schema_publish_file_service_is_lazily_created(self, base_config):
        client = self._client_with_mock_loader(base_config)
        assert client.schema_publish_file_service is not None

    def test_dataset_file_service_is_lazily_created(self, base_config):
        client = self._client_with_mock_loader(base_config)
        assert client.dataset_file_service is not None

    def test_build_file_service_passes_correct_bucket(self, base_config):
        client = self._client_with_mock_loader(base_config)
        svc = client._build_file_service(Bucket.DATASET_BUCKET)
        client.__dict__["bucket_loader"].fetch_bucket.assert_called_with(Bucket.DATASET_BUCKET)
        assert svc is not None


class TestSdsCommonConvenienceMethods:
    """generate_* convenience methods delegate to auth_header_provider."""

    def test_generate_authentication_headers_delegates(self, base_config):
        client = SdsCommon(config=base_config)
        mock_provider = MagicMock(spec=AuthHeaderProvider)
        mock_provider.generate.return_value = {"Authorization": "Bearer mytoken"}
        client.__dict__["auth_header_provider"] = mock_provider

        headers = client.generate_authentication_headers()

        mock_provider.generate.assert_called_once()
        assert headers == {"Authorization": "Bearer mytoken"}

    def test_generate_authentication_headers_by_impersonation_delegates(self, base_config):
        client = SdsCommon(config=base_config)
        mock_provider = MagicMock(spec=AuthHeaderProvider)
        mock_provider.generate_by_impersonation.return_value = {"Authorization": "Bearer imp-token"}
        client.__dict__["auth_header_provider"] = mock_provider

        headers = client.generate_authentication_headers_by_impersonation()

        mock_provider.generate_by_impersonation.assert_called_once()
        assert headers == {"Authorization": "Bearer imp-token"}
