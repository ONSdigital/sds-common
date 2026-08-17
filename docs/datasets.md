# Dataset operations

The library provides typed access to SDS dataset metadata.

---

## Fetching dataset metadata

```python
from sds_common import SdsCommon

client = SdsCommon()

datasets = client.sds_dataset_request_service.get_dataset_metadata(
    survey_id="068",
    period_id="202301",
)

for dataset in datasets:
    print(dataset.dataset_id)
    print(dataset.filename)
    print(dataset.total_reporting_units)
```

The method returns a list of `DatasetMetadata` objects.

---

## `DatasetMetadata` fields

| Field | Type | Description |
|---|---|---|
| `dataset_id` | `str` | Unique ID of the dataset |
| `survey_id` | `str` | The survey this dataset belongs to |
| `period_id` | `str` | The period this dataset covers |
| `form_types` | `list[str]` | Form types included in the dataset |
| `sds_published_at` | `str` | ISO 8601 timestamp of when the dataset was published |
| `total_reporting_units` | `int` | Number of reporting units in the dataset |
| `sds_dataset_version` | `int` | Version number of the dataset |
| `filename` | `str` | Name of the dataset file in GCS |
| `title` | `str \| None` | Optional human-readable title |

---

## Errors

| Exception | When raised |
|---|---|
| `DatasetMetadataRetrievalError` | SDS returned a non-200 response for the dataset metadata request |

```python
from sds_common import SdsCommon, DatasetMetadataRetrievalError

client = SdsCommon()

try:
    datasets = client.sds_dataset_request_service.get_dataset_metadata("068", "202301")
except DatasetMetadataRetrievalError as e:
    print(e.message)
```

`DatasetMetadataRetrievalError` is a subclass of `DatasetPublishError`.
