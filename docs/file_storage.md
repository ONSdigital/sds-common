← [Dataset operations](datasets.md) | [Back to README](../README.md) | **Next →** [Pub/Sub messaging](pub_sub.md)

---

# File storage (GCS)

Three GCS file services are available via `SdsCommon`, one per bucket.

---

## Available file services

| Property | Bucket | Configured by |
|---|---|---|
| `schema_file_service` | Published schemas | [`SCHEMA_BUCKET_NAME`](configuration.md#all-environment-variables) |
| `schema_staging_file_service` | Schemas awaiting publishing | [`SCHEMA_STAGING_BUCKET_NAME`](configuration.md#all-environment-variables) |
| `dataset_file_service` | Datasets | [`DATASET_BUCKET_NAME`](configuration.md#all-environment-variables) |

---

## Uploading a file

```python
from sds_common import SdsCommon

client = SdsCommon()
client.schema_staging_file_service.upload_file("/local/path/to/068_1.json")
```

The local filename is used as the GCS object name.

---

## Retrieving a JSON file

```python
data = client.schema_file_service.retrieve_json_file("068_1.json")
# Returns the file contents as a Python dict
```

---

## Checking a file exists

```python
exists = client.schema_file_service.check_file_exists("068_1.json")
# Returns True or False
```

---

## Deleting a file

```python
client.schema_staging_file_service.delete_file("068_1.json")
```

---

## Errors

| Exception | When raised |
|---|---|
| `BucketNotFoundError` | The GCS bucket named in config does not exist |

`BucketNotFoundError` is raised when a file service is first accessed — if the bucket name in config is wrong, it will fail at that point rather than at the file operation. See [Error handling](error_handling.md#bucketnotfounderror) for full details.

```python
from sds_common import SdsCommon, BucketNotFoundError

client = SdsCommon()

try:
    client.schema_file_service.upload_file("my_schema.json")
except BucketNotFoundError as e:
    print(f"Bucket not found: {e.bucket_name}")
```

---

← [Dataset operations](datasets.md) | [Back to README](../README.md) | **Next →** [Pub/Sub messaging](pub_sub.md)
