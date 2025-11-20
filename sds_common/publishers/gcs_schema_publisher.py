from sds_common.enums.buckets import Bucket
from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.repositories.bucket_loader import BucketLoader
from sds_common.services.bucket_service import BucketService


class GcsSchemaPublisher(SchemaPublisher):
    def __init__(self):
        super().__init__()
        self.bucket_service = BucketService(Bucket.SCHEMA_PUBLISH_BUCKET, BucketLoader())

    def _retrieve_schema(self, file_name: str):
        return self.bucket_service.retrieve_json_file_from_bucket(file_name)

    def cleanup(self, schema_file_name: str):
        self.bucket_service.delete_file_from_bucket(schema_file_name)
