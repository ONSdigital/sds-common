# Authentication

SDS endpoints are protected by Google Cloud IAP (Identity-Aware Proxy). This library provides two strategies for generating the required Bearer-token headers.

---

## How IAP authentication works

Every request to an IAP-secured endpoint needs an `Authorization: Bearer <token>` header. The token is a short-lived OpenID Connect ID token (typically ~1 hour) issued for a specific OAuth client ID. That client ID is stored in GCP Secret Manager and read at runtime.

`sds-common` handles this end-to-end. You never need to manage tokens yourself.

---

## Using `SdsCommon` (recommended)

The simplest approach — just access any authenticated service and the headers are generated automatically:

```python
from sds_common import SdsCommon

client = SdsCommon()

# authenticated_http_service generates a fresh token on every access
response = client.authenticated_http_service.make_get_request("https://my-service/api")

# Or use the convenience methods directly
headers = client.generate_authentication_headers()
headers = client.generate_authentication_headers_by_impersonation()
```

`authenticated_http_service` is a plain `@property` (not cached), so each call generates a fresh token. The underlying `requests.Session` with its retry adapter is reused.

---

## Strategy 1 — Metadata server (for GCP-hosted environments)

Use `generate()` when running inside GCP (Cloud Run, Cloud Functions, GCE, etc.) where the metadata server is reachable:

```python
headers = client.generate_authentication_headers()
# {"Authorization": "Bearer <token>", "Content-Type": "application/json"}
```

This calls the GCP metadata server directly to obtain an ID token for the IAP audience (the OAuth client ID). No local credentials are needed.

---

## Strategy 2 — IAM impersonation (for local development)

Use `generate_by_impersonation()` when running locally. It impersonates the App Engine default service account via IAM:

```python
headers = client.generate_authentication_headers_by_impersonation()
```

**Requirements:**
- Application Default Credentials (ADC) must be configured (`gcloud auth application-default login`)
- Your ADC account must hold the `Service Account Token Creator` IAM role on the App Engine default service account (`{PROJECT_ID}@appspot.gserviceaccount.com`)
- The `google-cloud-iam` package must be installed:
  ```bash
  pip install google-cloud-iam
  ```

---

## Using `AuthHeaderProvider` directly

If you only need authentication headers (e.g. in a test helper) and do not want the full `SdsCommon` facade:

```python
from sds_common import AuthHeaderProvider, SecretService, get_config

config = get_config()
secret_service = SecretService(config=config)
provider = AuthHeaderProvider(secret_service=secret_service, config=config)

headers = provider.generate()
```

This is the minimum instantiation — only `SecretService` and `AuthHeaderProvider` are created.

---

## `SecretService`

`SecretService` reads the IAP OAuth client ID from GCP Secret Manager. It is used internally by `AuthHeaderProvider` but can be used independently if you need to read secrets:

```python
from sds_common import SecretService

secret_service = SecretService()
oauth_client_id = secret_service.get_oauth_client_id()
```

The secret must be a JSON object with the structure:
```json
{
  "web": {
    "client_id": "your-oauth-client-id.apps.googleusercontent.com"
  }
}
```

The secret ID is configured via the `IAP_SECRET_ID` environment variable (default: `iap-secret`).

---

## Errors

| Exception | When raised |
|---|---|
| `SecretAccessError` | GCP Secret Manager is unreachable or returns an error |
| `SecretKeyError` | The `web.client_id` key is missing from the secret payload |

```python
from sds_common import SdsCommon, SecretAccessError, SecretKeyError

client = SdsCommon()
try:
    headers = client.generate_authentication_headers()
except SecretAccessError as e:
    print(f"Could not read secret: {e.error_detail}")
except SecretKeyError:
    print("Secret payload is missing the OAuth client ID key")
```
