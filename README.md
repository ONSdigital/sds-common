# sds-common

# sds-common

`sds-common` is a Python package that provides shared functionality and utilities for the Supplementary Data Service (SDS) application. It includes modules for configuration management, logging, error handling, and other common tasks that are used across different components of the SDS system.

## Usage

### Configuration

The library is configured via environment variables:

| Variable | Description |
|---|---|
| `PROJECT_ID` | GCP project ID |
| `SCHEMA_BUCKET_NAME` | GCS bucket name for schemas |
| `DATASET_BUCKET_NAME` | GCS bucket name for datasets |
| `AUTHDOMAIN` | IAP audience domain |
| `AUTHCLIENTID` | IAP client ID |
| `AUTHSERVICEACCOUNTFILE` | Path to service account key file |
| `GITHUB_SCHEMA_URL` | Base URL for GitHub schema files |
| `SDS_APPLICATION_URL` | SDS API base URL |
| `LOG_LEVEL` | Log level (default: `INFO`) |

### Quickstart

```python
from sds_common import SdsCommon

# Initialise the facade once; services are only created when first accessed
client = SdsCommon()

# Publish a schema from GitHub to SDS
response = client.github_schema_publisher.publish_schema("my_schema.json")

# Retrieve schema metadata
metadata = client.sds_schema_request_service.get_schema_metadata("survey_123")

# Make an authenticated request to an IAP-protected endpoint
http = client.authenticated_http_service
response = http.get("https://my-iap-service.example.com/api/resource")
```

### Generating IAP authentication headers only

If you only need auth headers (e.g. in an integration test helper), you can initialise
just the `AuthHeaderProvider` without spinning up the full client:

```python
from sds_common import AuthHeaderProvider, get_config

provider = AuthHeaderProvider(config=get_config())
headers = provider.generate()   # {"Authorization": "Bearer <token>"}
```

### Error handling

All library errors subclass standard built-in exceptions and are importable from the package root:

```python
from sds_common import (
    SdsAuthError,        # base for authentication errors
    SecretAccessError,   # GCP Secret Manager access failure
    SchemaPublishError,  # base for schema publishing errors
    SchemaFetchError,    # schema could not be fetched
    BucketNotFoundError, # GCS bucket not found
    EnvironmentVariableError,  # required env var missing
)
```

