# File storage (GCS)

The library provides a `FileService` for each of the three GCS buckets used by SDS. All three are accessible via `SdsCommon` and expose the same interface.

---

## Available file services

| Property | Bucket | Configured by |
|---|---|---|
| `schema_file_service` | Published schemas | `SCHEMA_BUCKET_NAME` |
| `schema_staging_file_service` | Schemas staged for publishing | `SCHEMA_STAGING_BUCKET_NAME` |
| `dataset_file_service` | Datasets | `DATASET_BUCKET_NAME` |

---

## Uploading a file

```python
from sds_common import SdsCommon

client = SdsCommon()
client.schema_staging_file_service.upload_file("/local/path/to/068_1.json")
```

The file is uploaded using the local filename as the GCS object name.

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

This is used by `GcsSchemaPublisher.cleanup()` to remove staged schema files after a successful publish.

---

## Errors

| Exception | When raised |
|---|---|
| `BucketNotFoundError` | The GCS bucket named in config does not exist |

```python
from sds_common import SdsCommon, BucketNotFoundError

client = SdsCommon()

try:
    client.schema_file_service.upload_file("my_schema.json")
except BucketNotFoundError as e:
    print(f"Bucket not found: {e.bucket_name}")
```

`BucketNotFoundError` is raised when the `FileService` is first accessed (i.e. when `SdsCommon` tries to load the bucket from GCS). If the bucket name is wrong it will fail at that point, not at the file operation.

---

## Using `BucketLoader` directly

If you need to load a bucket yourself:

```python
from google.cloud import storage
from sds_common import BucketLoader, Bucket, get_config

config = get_config()
loader = BucketLoader(storage_client=storage.Client(project=config.PROJECT_ID), config=config)

schema_bucket = loader.fetch_bucket(Bucket.SCHEMA_BUCKET)
```

Available `Bucket` enum values:

| Value | Bucket |
|---|---|
| `Bucket.SCHEMA_BUCKET` | Published schema bucket |
| `Bucket.SCHEMA_PUBLISH_BUCKET` | Schema staging bucket |
| `Bucket.DATASET_BUCKET` | Dataset bucket |
