# sds-common

# sds-common

`sds-common` is a Python library that provides a single, easy-to-use client for interacting with the Supplementary Data Service (SDS) and common GCP infrastructure. It handles authentication, schema publishing, dataset retrieval, file storage, Pub/Sub messaging, and Firestore access — all behind a single facade class that lazily initialises only what you need.

---

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [The `SdsCommon` facade](#the-sdscommon-facade)
- [Documentation by topic](#documentation-by-topic)

---

## Installation

```bash
pip install sds-common
```

All GCP client libraries are included as dependencies. The optional IAM impersonation feature requires `google-cloud-iam` to be installed separately (see [Authentication](docs/authentication.md)).

---

## Quick start

```python
from sds_common import SdsCommon

client = SdsCommon()

# Fetch schema metadata for a survey
metadata = client.sds_schema_request_service.get_schema_metadata("068")

# Publish a schema from GitHub to SDS
response = client.github_schema_publisher.publish_schema("068_1.json")

# Upload a file to the schema GCS bucket
client.schema_file_service.upload_file("/path/to/local/schema.json")

# Send a Pub/Sub message
client.pub_sub_service.send_message('{"event": "schema_published"}', topic_id="my-topic")
```

Nothing is initialised until first access. If you only need auth headers, only `SecretService` and `AuthHeaderProvider` are created — no GCS clients, no Firestore connections, nothing else.

---

## Configuration

The library is configured entirely through environment variables. All variables have sensible defaults for the `ons-sds-sandbox` project so tests and local development work out of the box.

| Environment variable | Default | Description |
|---|---|---|
| `PROJECT_ID` | `ons-sds-sandbox` | GCP project ID |
| `SDS_URL` | `test_url` | Base URL of the SDS API |
| `SDS_LOADER_URL` | `test_url` | Base URL of the loader service |
| `HTTP_REQUEST_TIMEOUT_SECONDS` | `540` | HTTP request timeout in seconds |
| `IAP_SECRET_ID` | `iap-secret` | GCP Secret Manager secret ID for the IAP OAuth credential |
| `GITHUB_SCHEMA_BASE_URL` | `https://raw.githubusercontent.com/ONSdigital/sds-schema-definitions/main/` | Base URL for raw schema files on GitHub |
| `POST_SCHEMA_PATH` | `/v1/schema` | SDS endpoint for posting a new schema |
| `GET_SCHEMA_METADATA_PATH` | `/v1/schema_metadata` | SDS endpoint for fetching schema metadata |
| `GET_ALL_SCHEMA_METADATA_PATH` | `/v1/all_schema_metadata` | SDS endpoint for fetching all schema metadata |
| `GET_DATASET_METADATA_PATH` | `/v1/dataset_metadata` | SDS endpoint for fetching dataset metadata |
| `DATASET_CREATE_PATH` | `/events/dataset/create` | SDS endpoint for creating a dataset |
| `DATASET_DELETE_PATH` | `/events/dataset/delete` | SDS endpoint for deleting a dataset |
| `PUBLISH_SCHEMA_ERROR_TOPIC_ID` | `ons-sds-publish-schema-fail` | Pub/Sub topic for schema publish failures |
| `PUBLISH_SCHEMA_SUCCESS_TOPIC_ID` | `ons-sds-publish-schema` | Pub/Sub topic for schema publish successes |
| `PUBLISH_SCHEMA_QUEUE_TOPIC_ID` | `schema-publish-queue` | Pub/Sub topic for the schema publish queue |
| `PUBLISH_DATASET_TOPIC_ID` | `ons-sds-publish-dataset` | Pub/Sub topic for dataset publishing |
| `FIRESTORE_DB_NAME` | `{PROJECT_ID}-sds` | Firestore database name |
| `SCHEMA_BUCKET_NAME` | `{PROJECT_ID}-sds-europe-west2-schema` | GCS bucket for published schemas |
| `SCHEMA_STAGING_BUCKET_NAME` | `{PROJECT_ID}-sds-europe-west2-schema-publish` | GCS bucket for schemas awaiting publishing |
| `DATASET_BUCKET_NAME` | `{PROJECT_ID}-sds-europe-west2-dataset` | GCS bucket for datasets |
| `LOG_LEVEL` | `INFO` | Log level for the host application (see `get_log_level()`) |

---

## The `SdsCommon` facade

`SdsCommon` is the single entry point for the library. Instantiate it once; every property is lazily created on first access and then cached for the lifetime of the instance.

```python
from sds_common import SdsCommon

client = SdsCommon()
```

You can also supply a pre-built `Config` instance, which is useful in tests:

```python
from sds_common import SdsCommon, Config

client = SdsCommon(config=my_config)
```

### Available properties

| Property | Type | Description |
|---|---|---|
| `config` | `Config` | Resolved configuration object |
| `secret_service` | `SecretService` | Reads secrets from GCP Secret Manager |
| `auth_header_provider` | `AuthHeaderProvider` | Generates IAP Bearer-token headers |
| `http_service` | `HttpService` | Unauthenticated HTTP client (e.g. GitHub requests) |
| `authenticated_http_service` | `HttpService` | Authenticated HTTP client — fresh token on every access |
| `sds_schema_request_service` | `SdsSchemaRequestService` | HTTP calls to SDS schema endpoints |
| `sds_dataset_request_service` | `SdsDatasetRequestService` | HTTP calls to SDS dataset endpoints |
| `schema_validator_service` | `SchemaValidatorService` | Validates a schema before publishing |
| `gcs_schema_publisher` | `GcsSchemaPublisher` | Publishes schemas from the GCS staging bucket to SDS |
| `github_schema_publisher` | `GithubSchemaPublisher` | Fetches schemas from GitHub, validates, and publishes to SDS |
| `schema_file_service` | `FileService` | File operations on the schema GCS bucket |
| `schema_publish_file_service` | `FileService` | File operations on the schema-publish staging GCS bucket |
| `dataset_file_service` | `FileService` | File operations on the dataset GCS bucket |
| `pub_sub_service` | `PubSubService` | Publishes messages to GCP Pub/Sub topics |
| `firestore_client` | `firestore.Client` | Raw Firestore client |
| `firebase_loader` | `FirebaseLoader` | Typed wrapper around Firestore for schema collection access |
| `bucket_loader` | `BucketLoader` | Loads GCS `Bucket` objects by `Bucket` enum value |

### Convenience methods

| Method | Returns | Description |
|---|---|---|
| `generate_authentication_headers()` | `dict[str, str]` | IAP headers via GCP metadata server |
| `generate_authentication_headers_by_impersonation()` | `dict[str, str]` | IAP headers via IAM service account impersonation |

---

## Documentation by topic

Detailed guides for each area of the library:

| Guide | What it covers |
|---|---|
| [Authentication](docs/authentication.md) | Generating IAP headers, metadata server vs impersonation, `SecretService` |
| [Schema operations](docs/schemas.md) | Fetching metadata, posting schemas, publishing from GitHub or GCS |
| [Dataset operations](docs/datasets.md) | Fetching dataset metadata |
| [File storage (GCS)](docs/file_storage.md) | Uploading, downloading, and deleting files across GCS buckets |
| [Pub/Sub messaging](docs/pub_sub.md) | Sending messages to Pub/Sub topics |
| [Firestore](docs/firestore.md) | Accessing the Firestore database and schema collection |
| [Error handling](docs/error_handling.md) | Full exception hierarchy and how to catch specific errors |
| [Testing helpers](docs/testing_helpers.md) | `PubSubHelper` and `FirebaseLoader` for integration tests |
| [Configuration reference](docs/configuration.md) | All environment variables, overriding config in tests |


