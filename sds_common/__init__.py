"""
sds-common
==========

A shared library for interacting with the SDS (Survey Data Service) API
and publishing schemas.

Quickstart
----------
    from sds_common import SdsClient, Bucket

    client = SdsClient()

    # Query SDS
    client.get_schema_metadata("survey_123")
    client.get_all_schema_metadata()
    client.get_dataset_metadata("survey_123", "202401")

    # Publish a schema from GitHub
    client.publish_schema_from_github("schemas/survey_123_v1.json")

    # Publish a schema from GCS
    client.publish_schema_from_gcs("survey_123_v1.json")
    client.publish_schema_from_gcs("survey_123_v1.json", bucket=Bucket.SCHEMA_BUCKET)

    # Publish from GCS and clean up the source file afterwards
    client.publish_schema_from_gcs_and_cleanup("survey_123_v1.json")
"""

# --- Main client ---
from sds_common.sds_facade import SdsClient

# --- Enums ---
from sds_common.enums.buckets import Bucket

# --- Models ---
from sds_common.models.dataset_models import DatasetMetadata

# --- Errors (re-exported so callers can catch them without digging into sub-modules) ---
from sds_common.models.schema_publish_errors import (
    SchemaPublishError,
    FilepathError,
    SchemaDuplicationError,
    SchemaVersionMismatchError,
    SurveyIDError,
    SchemaVersionError,
    SchemaJSONDecodeError,
    SchemaFetchError,
    SchemaPostError,
    SchemaMetadataError,
    SecretAccessError,
    SecretKeyError,
)
from sds_common.models.dataset_publish_errors import (
    DatasetPublishError,
    DatasetMetadataRetrievalError,
    DatasetCreateError,
)

__all__ = [
    # Client
    "SdsClient",
    # Enums
    "Bucket",
    # Models
    "DatasetMetadata",
    # Schema errors
    "SchemaPublishError",
    "FilepathError",
    "SchemaDuplicationError",
    "SchemaVersionMismatchError",
    "SurveyIDError",
    "SchemaVersionError",
    "SchemaJSONDecodeError",
    "SchemaFetchError",
    "SchemaPostError",
    "SchemaMetadataError",
    "SecretAccessError",
    "SecretKeyError",
    # Dataset errors
    "DatasetPublishError",
    "DatasetMetadataRetrievalError",
    "DatasetCreateError",
]

