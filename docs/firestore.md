# Firestore

Access to Firestore is available via `SdsCommon`.

---

## Accessing the schemas collection

```python
from sds_common import SdsCommon

client = SdsCommon()

schemas = client.firestore.get_schemas_collection()

# Stream all documents
for doc in schemas.stream():
    print(doc.id, doc.to_dict())

# Get a specific document
doc = schemas.document("068").get()
if doc.exists:
    print(doc.to_dict())
```

---

## Raw Firestore client

If you need to query a collection outside of `schemas`, use the raw client:

```python
client.firestore_client.collection("my_collection").stream()
```

The client connects to the database configured by `FIRESTORE_DB_NAME` (default: `{PROJECT_ID}-sds`).
