# Schema operations

The library provides two ways to publish schemas to SDS and several methods for querying existing schema metadata.

---

## Fetching schema metadata

### For a specific survey

```python
from sds_common import SdsCommon

client = SdsCommon()

# Returns a list of metadata dicts, or None if the survey does not exist
metadata = client.sds_schema_request_service.get_schema_metadata("068")

if metadata is None:
    print("No schemas found for this survey")
else:
    for entry in metadata:
        print(entry)
```

### All schemas

```python
all_metadata = client.sds_schema_request_service.get_all_schema_metadata()
# Returns a list of all schema metadata dicts
```

---

## Publishing a schema from GitHub

`GithubSchemaPublisher` fetches a schema file from the configured GitHub URL, validates it, and posts it to SDS.

```python
from sds_common import SdsCommon

client = SdsCommon()
response = client.github_schema_publisher.publish_schema("068_1.json")
print(response.status_code)  # 200 on success
```

The file is fetched from `GITHUB_SCHEMA_URL + file_name` using an **unauthenticated** HTTP client (GitHub raw content is public). The schema is then validated against existing SDS metadata before being posted.

**What validation checks:**
- The schema JSON contains a `survey_id` and `schema_version`
- The `schema_version` matches the version number in the filename
- The version does not already exist in SDS (duplicate prevention)

---

## Publishing a schema from GCS

`GcsSchemaPublisher` reads a schema file from the GCS staging bucket (`SCHEMA_PUBLISH_BUCKET_NAME`), posts it to SDS, and optionally cleans up the staged file afterwards.

```python
from sds_common import SdsCommon

client = SdsCommon()

# Publish and then remove the staged file
response = client.gcs_schema_publisher.publish_schema("068_1.json")
client.gcs_schema_publisher.cleanup("068_1.json")
```

Unlike `GithubSchemaPublisher`, `GcsSchemaPublisher` does **not** run the version duplication check — it is assumed the file has already been validated before staging.

---

## Posting a schema directly

If you have already built a `Schema` object and want to post it without going through a publisher:

```python
from sds_common import SdsCommon
from sds_common.schema.schema import Schema

client = SdsCommon()

schema_json = {"properties": {"survey_id": {"enum": ["068"]}, "schema_version": {"const": "1"}}, ...}
schema = Schema.set_schema(schema_json, filepath="068_1.json")

response = client.sds_schema_request_service.post_schema(schema)
```

---

## Errors

| Exception | When raised |
|---|---|
| `SchemaFetchError` | GitHub returned a non-200 response when fetching the schema |
| `SchemaJSONDecodeError` | The fetched content could not be parsed as JSON |
| `SurveyIDError` | The schema JSON does not contain a `survey_id` |
| `SchemaVersionError` | The schema JSON does not contain a `schema_version` |
| `SchemaVersionMismatchError` | The version in the JSON does not match the version in the filename |
| `SchemaDuplicationError` | A schema with this version already exists in SDS |
| `SchemaMetadataError` | SDS returned a non-200/404 response for a metadata request |
| `SchemaMetadataFormatError` | The metadata response body was not in the expected list format |
| `SchemaPostError` | SDS returned a non-200 response when posting the schema |
| `FilepathError` | The filepath could not be parsed to extract a filename |

All of these are subclasses of `SchemaPublishError` and include a `generate_message_content()` method that serialises the error as JSON — useful for publishing failure events to Pub/Sub:

```python
from sds_common import SdsCommon, SchemaPublishError

client = SdsCommon()

try:
    client.github_schema_publisher.publish_schema("068_1.json")
except SchemaPublishError as e:
    # Publish the error details to the failure topic
    client.pub_sub_service.send_message(
        e.generate_message_content(),
        topic_id=client.config.PUBLISH_SCHEMA_ERROR_TOPIC_ID,
    )
```
