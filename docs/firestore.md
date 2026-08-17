# Firestore

The library exposes the Firestore client and a typed `FirebaseLoader` helper for accessing the SDS schemas collection.

---

## Accessing the Firestore client

```python
from sds_common import SdsCommon

client = SdsCommon()

# Raw Firestore client — use for any arbitrary collection
firestore_client = client.firestore_client
```

The client is connected to the database configured by `FIRESTORE_DB_NAME` (default: `{PROJECT_ID}-sds`).

---

## Using `FirebaseLoader`

`FirebaseLoader` is a thin wrapper that pre-loads the `schemas` Firestore collection:

```python
from sds_common import SdsCommon

client = SdsCommon()
loader = client.firestore

# Get the raw Firestore client
firestore_client = loader.get_client()

# Get the pre-loaded schemas collection reference
schemas_collection = loader.get_schemas_collection()

# Query the schemas collection directly
docs = schemas_collection.stream()
for doc in docs:
    print(doc.id, doc.to_dict())
```

`FirebaseLoader` is primarily intended for integration test helpers that need to inspect Firestore state after SDS operations.
