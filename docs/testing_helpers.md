# Testing helpers

`sds-common` includes helpers specifically designed for integration tests that need to interact with real GCP infrastructure (Pub/Sub, Firestore).

---

## `PubSubHelper`

`PubSubHelper` manages the lifecycle of a Pub/Sub subscriber for a test, and provides methods to read and assert on messages published during the test.

### Setup

```python
from google.cloud import pubsub_v1
from sds_common import PubSubHelper

helper = PubSubHelper(
    topic_id="my-topic",
    subscriber_client=pubsub_v1.SubscriberClient(),
    publisher_client=pubsub_v1.PublisherClient(),
    project_id="my-gcp-project",
)
```

### Typical integration test pattern

```python
SUBSCRIBER_ID = "my-test-subscriber"

# Before the test: create the subscriber and drain any leftover messages
helper.try_create_subscriber(SUBSCRIBER_ID)
helper.purge_messages(SUBSCRIBER_ID)

# Run the action under test
trigger_some_schema_publish()

# Assert on the messages produced
messages = helper.pull_and_acknowledge_messages(SUBSCRIBER_ID)
assert messages is not None
assert messages[0]["survey_id"] == "068"

# After the test: clean up
helper.try_delete_subscriber(SUBSCRIBER_ID)
```

### Method reference

| Method | Description |
|---|---|
| `try_create_subscriber(subscriber_id)` | Creates the subscription if it does not exist; polls until confirmed active. Raises `RuntimeError` if it cannot be confirmed after retries. |
| `try_delete_subscriber(subscriber_id)` | Deletes the subscription if it exists; polls until confirmed gone. Raises `RuntimeError` if it cannot be confirmed deleted after retries. |
| `publish_message(message)` | Publishes a raw string message to the topic. |
| `pull_and_acknowledge_messages(subscriber_id)` | Pulls up to 5 messages, acknowledges them, and returns them as `list[dict]`. Returns `None` if no messages were available. |
| `purge_messages(subscriber_id)` | Seeks the subscription to a far-future timestamp, effectively discarding all pending messages. |
| `format_received_message_data(received_message)` | Decodes a raw Pub/Sub message into a `dict`. |

### Notes

- `try_create_subscriber` skips creation if the subscription already exists (idempotent).
- The retry loop for create/delete uses exponential backoff starting at 0.5 s with 5 attempts.
- An unexpected error during subscription existence checks is logged as a warning with the full stack trace rather than being swallowed silently.

---

## `FirebaseLoader`

`FirebaseLoader` provides typed access to Firestore for test assertions. It is available via `SdsCommon` or can be instantiated directly.

```python
from sds_common import SdsCommon

client = SdsCommon()
loader = client.firebase_loader

# Check a document exists in the schemas collection
schemas = loader.get_schemas_collection()
doc = schemas.document("068").get()
assert doc.exists
```

See [Firestore](firestore.md) for more detail.

---

## Writing unit tests for code that uses `sds-common`

### Clearing config cache between tests

`get_config()` uses `@lru_cache`. If you are patching environment variables in unit tests, clear the cache before each test to avoid cross-test pollution:

```python
import pytest
from sds_common.config.config import get_config

@pytest.fixture(autouse=True)
def clear_config_cache():
    get_config.cache_clear()
    yield
    get_config.cache_clear()
```

### Pre-populating `@cached_property` in tests

`SdsCommon` properties are `@cached_property`. The simplest way to inject a mock is to write it directly into the instance's `__dict__`, which bypasses the descriptor:

```python
from unittest.mock import MagicMock
from sds_common import SdsCommon

def test_something():
    client = SdsCommon()
    mock_service = MagicMock()
    client.__dict__["sds_schema_request_service"] = mock_service

    # Now client.sds_schema_request_service returns mock_service
```

### `authenticated_http_service` is a plain `@property`

Because `authenticated_http_service` generates a fresh token on every access it is a `@property`, not `@cached_property`. You cannot pre-populate it via `__dict__`. Instead, inject a mock `auth_header_provider` and `_authenticated_session`:

```python
from unittest.mock import MagicMock, patch
from sds_common import SdsCommon

def test_authenticated_http():
    client = SdsCommon()
    mock_provider = MagicMock()
    mock_provider.generate.return_value = {"Authorization": "Bearer test-token"}
    client.__dict__["auth_header_provider"] = mock_provider
    client.__dict__["_authenticated_session"] = MagicMock()

    http = client.authenticated_http_service
    # http is now constructed with the mock session and headers
```
