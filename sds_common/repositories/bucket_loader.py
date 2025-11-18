from sds_common.config.config import CONFIG
from google.cloud import exceptions, storage
from sds_common.enums.buckets import Bucket

class BucketLoader:

    def __init__(self):
        self._client = storage.Client(project=CONFIG.PROJECT_ID)

    def fetch_bucket(self, bucket: Bucket) -> storage.Bucket:
        """
        Lazily fetches and caches the specified bucket from Google Cloud Storage.
        """
        if not isinstance(bucket, Bucket):
            raise TypeError(f"Expected bucket to be an instance of Bucket enum, got {type(bucket)}")

        attr_name = bucket.name.lower()

        if not hasattr(self, attr_name):
            try:
                bucket_instance = self._client.get_bucket(bucket.value)
                setattr(self, attr_name, bucket_instance)
            except exceptions.NotFound as exc:
                raise Exception(f"Bucket {bucket.value} not found") from exc
        return getattr(self, attr_name)
