from sds_common.config.config import CONFIG
from sds_common.enums.buckets import Bucket
from sds_common.interfaces.http_service_interface import HttpServiceInterface
from sds_common.interfaces.secret_service_interface import SecretServiceInterface
from sds_common.publishers.gcs_schema_publisher import GcsSchemaPublisher
from sds_common.publishers.github_schema_publisher import GithubSchemaPublisher
from sds_common.repositories.bucket_file_repository import BucketFileRepository
from sds_common.repositories.bucket_loader import BucketLoader
from sds_common.services.gcp_file_service import GcpFileService
from sds_common.services.gcp_secret_service import GcpSecretService
from sds_common.services.http_service import HttpService
from sds_common.services.pub_sub_service import PubSubService
from sds_common.services.schema_validator_service import SchemaValidatorService
from sds_common.services.sds_request_service import SdsRequestService


# --- Repositories ---

def get_bucket_loader() -> BucketLoader:
    return BucketLoader()


def get_bucket_file_repository(bucket: Bucket) -> BucketFileRepository:
    return BucketFileRepository(get_bucket_loader().fetch_bucket(bucket))


# --- HTTP ---

def get_gcp_secret_service() -> SecretServiceInterface:
    return GcpSecretService()


def get_authenticated_http_service() -> HttpServiceInterface:
    """HttpService with GCP authentication headers — used for all SDS interactions."""
    return HttpService.create(authentication_headers=True, secret_service=get_gcp_secret_service())


def get_unauthenticated_http_service() -> HttpServiceInterface:
    """HttpService without authentication headers — used for public external requests (e.g. GitHub)."""
    return HttpService.create(authentication_headers=False)


# --- Services ---

def get_sds_request_service() -> SdsRequestService:
    """SDS API interactions are always authenticated."""
    return SdsRequestService(
        http_service=get_authenticated_http_service(),
        sds_url=CONFIG.SDS_URL,
    )


def get_schema_validator_service() -> SchemaValidatorService:
    return SchemaValidatorService(sds_request_service=get_sds_request_service())


def get_gcp_file_service(bucket: Bucket) -> GcpFileService:
    return GcpFileService(bucket, get_bucket_loader())


def get_pub_sub_service() -> PubSubService:
    return PubSubService()


# --- Publishers ---

def get_github_schema_publisher() -> GithubSchemaPublisher:
    """
    Schema retrieval from GitHub is unauthenticated (handled internally by fetch_raw_schema_from_github).
    Posting to SDS is authenticated via the injected SdsRequestService.
    """
    sds_request_service = get_sds_request_service()
    return GithubSchemaPublisher(
        sds_request_service=sds_request_service,
        validator=SchemaValidatorService(sds_request_service),
    )


def get_gcs_schema_publisher(bucket: Bucket) -> GcsSchemaPublisher:
    """GCS retrieval uses application default credentials; SDS posting is authenticated."""
    return GcsSchemaPublisher(
        sds_request_service=get_sds_request_service(),
        file_service=get_gcp_file_service(bucket),
    )
