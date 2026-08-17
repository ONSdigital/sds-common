← [File storage (GCS)](file_storage.md) | [Back to README](../README.md) | **Next →** [Firestore](firestore.md)

---

# Pub/Sub messaging

`PubSubService` provides a simple interface for publishing messages to GCP Pub/Sub topics.

---

## Sending a message

```python
from sds_common import SdsCommon

client = SdsCommon()

client.pub_sub_service.send_message(
    message='{"survey_id": "068", "schema_version": "1"}',
    topic_id="my-topic-id",
)
```

Messages must be JSON-encoded strings. The message is published to `projects/{PROJECT_ID}/topics/{topic_id}`.

---

## Using the pre-configured topic IDs

The config provides topic IDs for the standard SDS topics so you do not need to hardcode them. See the [configuration reference](configuration.md#all-environment-variables) for all available topic ID variables.

```python
config = client.config

# Publish a schema error event
client.pub_sub_service.send_message(
    message=error.generate_message_content(),
    topic_id=config.PUBLISH_SCHEMA_ERROR_TOPIC_ID,
)

# Publish a schema success event
client.pub_sub_service.send_message(
    message='{"filepath": "068_1.json"}',
    topic_id=config.PUBLISH_SCHEMA_SUCCESS_TOPIC_ID,
)

# Enqueue a schema for publishing
client.pub_sub_service.send_message(
    message='{"filepath": "068_1.json"}',
    topic_id=config.PUBLISH_SCHEMA_QUEUE_TOPIC_ID,
)

# Publish a dataset event
client.pub_sub_service.send_message(
    message='{"dataset_id": "abc123"}',
    topic_id=config.PUBLISH_DATASET_TOPIC_ID,
)
```

---

## Publishing schema errors on failure

A common pattern is to catch `SchemaPublishError` and publish the error details to the failure topic so they can be monitored. See [Schema operations → Errors](schemas.md#errors) for the full list of schema exceptions.

```python
from sds_common import SdsCommon, SchemaPublishError

client = SdsCommon()

try:
    client.github_publisher.publish_schema("068_1.json")
except SchemaPublishError as e:
    client.pub_sub_service.send_message(
        e.generate_message_content(),
        topic_id=client.config.PUBLISH_SCHEMA_ERROR_TOPIC_ID,
    )
    raise
```

`generate_message_content()` returns a JSON string with `error_type`, `message`, and `filepath` fields.

---

← [File storage (GCS)](file_storage.md) | [Back to README](../README.md) | **Next →** [Firestore](firestore.md)
