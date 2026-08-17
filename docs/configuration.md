# Configuration reference

All configuration is read from environment variables at the time `Config` is first instantiated. Every variable has a default so the library works out of the box for the `ons-sds-sandbox` project.

---

## How configuration works

`Config` is an instance class — not module-level globals. This means nothing is read from the environment until you actually create a `Config` object (or call `SdsCommon()`). This is intentional: it avoids surprising import-time failures and makes the library safe to import in any context.

```python
# Config is not read at import time
from sds_common import SdsCommon

# Config is read here, on first access
client = SdsCommon()
print(client.config.PROJECT_ID)
```

---

## `get_config()` and the `CONFIG` proxy

```python
from sds_common import get_config, CONFIG

# get_config() returns a cached singleton Config instance
config = get_config()

# CONFIG is a lazy proxy — identical to get_config() but usable
# as a module-level constant in legacy code
print(CONFIG.PROJECT_ID)
```

`get_config()` is cached with `@lru_cache(maxsize=1)`. The same `Config` instance is returned on every call within a process.

---

## All environment variables

| Variable | Default | Description |
|---|---|---|
| `PROJECT_ID` | `ons-sds-sandbox` | GCP project ID used for all GCP client connections |
| `SDS_URL` | `test_url` | Base URL of the SDS API (no trailing slash) |
| `LOADER_URL` | `test_url` | Base URL of the loader service |
| `PROCESS_TIMEOUT` | `540` | HTTP request timeout in seconds |
| `SECRET_ID` | `iap-secret` | GCP Secret Manager secret name containing the IAP OAuth credentials |
| `GITHUB_SCHEMA_URL` | `https://raw.githubusercontent.com/ONSdigital/sds-schema-definitions/main/` | Base URL for fetching schema files from GitHub |
| `POST_SCHEMA_URL` | `/v1/schema` | SDS path for `POST /schema` |
| `GET_SCHEMA_METADATA_URL` | `/v1/schema_metadata` | SDS path for `GET /schema_metadata` |
| `GET_ALL_SCHEMA_METADATA_URL` | `/v1/all_schema_metadata` | SDS path for `GET /all_schema_metadata` |
| `GET_DATASET_METADATA_URL` | `/v1/dataset_metadata` | SDS path for `GET /dataset_metadata` |
| `DATASET_CREATE_PATH` | `/events/dataset/create` | SDS path for the dataset create event |
| `DATASET_DELETE_PATH` | `/events/dataset/delete` | SDS path for the dataset delete event |
| `PUBLISH_SCHEMA_ERROR_TOPIC_ID` | `ons-sds-publish-schema-fail` | Pub/Sub topic ID for schema publish failure events |
| `PUBLISH_SCHEMA_SUCCESS_TOPIC_ID` | `ons-sds-publish-schema` | Pub/Sub topic ID for schema publish success events |
| `PUBLISH_SCHEMA_QUEUE_TOPIC_ID` | `schema-publish-queue` | Pub/Sub topic ID for the schema publish queue |
| `PUBLISH_DATASET_TOPIC_ID` | `ons-sds-publish-dataset` | Pub/Sub topic ID for dataset events |
| `FIRESTORE_DB_NAME` | `{PROJECT_ID}-sds` | Firestore database name |
| `SCHEMA_BUCKET_NAME` | `{PROJECT_ID}-sds-europe-west2-schema` | GCS bucket for published schema files |
| `SCHEMA_PUBLISH_BUCKET_NAME` | `{PROJECT_ID}-sds-europe-west2-schema-publish` | GCS bucket for schemas staged for publishing |
| `DATASET_BUCKET_NAME` | `{PROJECT_ID}-sds-europe-west2-dataset` | GCS bucket for dataset files |
| `LOG_LEVEL` | `INFO` | Log level string used by `get_log_level()` for host application log configuration |

---

## Overriding config in tests

### Option 1 — Patch environment variables

```python
import pytest
from unittest.mock import patch
from sds_common.config.config import get_config

@pytest.fixture(autouse=True)
def clear_config_cache():
    get_config.cache_clear()
    yield
    get_config.cache_clear()

def test_something(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "my-test-project")
    monkeypatch.setenv("SDS_URL", "https://test.sds.example.com")

    config = get_config()
    assert config.PROJECT_ID == "my-test-project"
```

> **Important:** Always call `get_config.cache_clear()` before and after each test to prevent the cached singleton leaking between tests.

### Option 2 — Pass a `Config` directly to `SdsCommon`

```python
from sds_common import SdsCommon, Config
from unittest.mock import MagicMock, patch

with patch.dict("os.environ", {"PROJECT_ID": "test-project", "SDS_URL": "http://localhost"}):
    config = Config()

client = SdsCommon(config=config)
```

### Option 3 — Mock the config object

```python
from unittest.mock import MagicMock
from sds_common import SdsCommon

mock_config = MagicMock()
mock_config.PROJECT_ID = "test-project"
mock_config.SDS_URL = "http://localhost"

client = SdsCommon(config=mock_config)
```

---

## `get_log_level()`

`get_log_level()` is a utility for **host applications** to configure their own logging. It reads the `LOG_LEVEL` environment variable and returns the corresponding `logging` integer constant:

```python
import logging
from sds_common.config.logging_config import get_log_level

logging.basicConfig(level=get_log_level())
```

`sds-common` itself uses `logging.getLogger(__name__)` throughout and does not configure any handlers — it follows the library logging best practice of leaving handler/level setup entirely to the host application.
