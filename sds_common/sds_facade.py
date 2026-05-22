"""
SdsClient — the main entry point for the sds-common package.

Usage:
    from sds_common import SdsClient

    client = SdsClient()

    # SDS API
    metadata = client.get_schema_metadata("survey_123")
    all_metadata = client.get_all_schema_metadata()
    dataset_metadata = client.get_dataset_metadata("survey_123", "202401")

    # Publishing
    client.publish_schema_from_github("schemas/survey_123_v1.json")
    client.publish_schema_from_gcs("survey_123_v1.json", Bucket.SCHEMA_PUBLISH_BUCKET)
"""
import requests

from sds_common.enums.buckets import Bucket
from sds_common.models.dataset_models import DatasetMetadata
from sds_common.publishers.gcs_schema_publisher import GcsSchemaPublisher
from sds_common.publishers.github_schema_publisher import GithubSchemaPublisher
from sds_common.services.schema_validator_service import SchemaValidatorService
from sds_common.services.sds_request_service import SdsRequestService
from sds_common.config.config import CONFIG
from sds_common.services.http_service import HttpService
from sds_common.services.gcp_secret_service import GcpSecretService
from sds_common.services.gcp_file_service import GcpFileService
from sds_common.repositories.bucket_loader import BucketLoader


class SdsClient:
    """
    High-level client for interacting with SDS.

    All dependencies are wired automatically from environment configuration.
    No manual setup is required — just instantiate and call methods.
    """

    def __init__(self):
        self._sds_request_service: SdsRequestService = self._build_sds_request_service()
        self._validator: SchemaValidatorService = SchemaValidatorService(self._sds_request_service)

    # ------------------------------------------------------------------
    # Internal wiring — kept private so callers never need to touch it
    # ------------------------------------------------------------------

    @staticmethod
    def _build_sds_request_service() -> SdsRequestService:
        secret_service = GcpSecretService()
        http_service = HttpService.create(
            authentication_headers=True,
            secret_service=secret_service,
        )
        return SdsRequestService(http_service=http_service, sds_url=CONFIG.SDS_URL)

    # ------------------------------------------------------------------
    # SDS API — schemas
    # ------------------------------------------------------------------

    def get_schema_metadata(self, survey_id: str) -> requests.Response:
        """
        Retrieve schema metadata for a given survey.

        :param survey_id: The survey ID to query.
        :return: The response from the SDS schema_metadata endpoint.
        """
        return self._sds_request_service.get_schema_metadata(survey_id)

    def get_all_schema_metadata(self) -> requests.Response:
        """
        Retrieve metadata for all schemas in SDS.

        :return: The response from the SDS all_schema_metadata endpoint.
        """
        return self._sds_request_service.get_all_schema_metadata()

    # ------------------------------------------------------------------
    # SDS API — datasets
    # ------------------------------------------------------------------

    def get_dataset_metadata(self, survey_id: str, period_id: str) -> list[DatasetMetadata]:
        """
        Retrieve dataset metadata for a given survey and period.

        :param survey_id: The survey ID.
        :param period_id: The period ID.
        :return: A list of DatasetMetadata objects.
        """
        return self._sds_request_service.get_dataset_metadata(survey_id, period_id)

    def get_dataset_create(self) -> requests.Response:
        """
        Trigger the dataset/create SDS endpoint.

        :return: The response from the dataset/create endpoint.
        """
        return self._sds_request_service.get_dataset_create()

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    def publish_schema_from_github(self, file_name: str) -> requests.Response:
        """
        Fetch a schema from the configured GitHub repository, validate it, and publish it to SDS.

        :param file_name: The path/filename of the schema within the GitHub repo
                          (e.g. ``"schemas/survey_123_v1.json"``).
        :return: The response from SDS.
        """
        publisher = GithubSchemaPublisher(
            sds_request_service=self._sds_request_service,
            validator=self._validator,
        )
        return publisher.publish_schema(file_name)

    def publish_schema_from_gcs(self, file_name: str, bucket: Bucket = Bucket.SCHEMA_PUBLISH_BUCKET) -> requests.Response:
        """
        Fetch a schema from a GCS bucket and publish it to SDS.

        :param file_name: The filename of the schema in the bucket.
        :param bucket: The GCS bucket to retrieve the schema from.
                       Defaults to ``Bucket.SCHEMA_PUBLISH_BUCKET``.
        :return: The response from SDS.
        """
        file_service = GcpFileService(bucket, BucketLoader())
        publisher = GcsSchemaPublisher(
            sds_request_service=self._sds_request_service,
            file_service=file_service,
        )
        return publisher.publish_schema(file_name)

    def publish_schema_from_gcs_and_cleanup(self, file_name: str, bucket: Bucket = Bucket.SCHEMA_PUBLISH_BUCKET) -> requests.Response:
        """
        Fetch a schema from a GCS bucket, publish it to SDS, then delete the file from the bucket.

        :param file_name: The filename of the schema in the bucket.
        :param bucket: The GCS bucket to retrieve the schema from.
                       Defaults to ``Bucket.SCHEMA_PUBLISH_BUCKET``.
        :return: The response from SDS.
        """
        file_service = GcpFileService(bucket, BucketLoader())
        publisher = GcsSchemaPublisher(
            sds_request_service=self._sds_request_service,
            file_service=file_service,
        )
        response = publisher.publish_schema(file_name)
        publisher.cleanup(file_name)
        return response
