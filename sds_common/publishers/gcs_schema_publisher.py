import requests
from sds_common.enums.buckets import Bucket
from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.repositories.bucket_loader import BucketLoader
from sds_common.schema.schema import Schema
from sds_common.services.bucket_service import BucketService


class GcsSchemaPublisher(SchemaPublisher):
    """
    Publisher for retrieving and publishing schemas from Google Cloud Storage (GCS) buckets.
    """
    def __init__(self):
        super().__init__()
        self.bucket_service = BucketService(Bucket.SCHEMA_PUBLISH_BUCKET, BucketLoader())

    def _retrieve_schema(self, file_name: str) -> dict:
        """
        Retrieve the schema JSON file from the GCS bucket.

        :param file_name: The name of the schema file to retrieve.
        :return: The schema as a dictionary.
        """
        return self.bucket_service.retrieve_json_file_from_bucket(file_name)

    def publish_schema(self, file_name: str) -> requests.Response:
        """
        Publish the schema retrieved from the GCS bucket.

        :param file_name: The name of the schema file to publish.
        :return: The response from the schema publishing service.
        """
        schema_json = self._retrieve_schema(file_name)
        schema = Schema.set_schema(schema_json, file_name)
        response = self.schema_request_service.post_schema(schema)
        return response

    def cleanup(self, schema_file_name: str):
        """
        Clean up the schema file from the GCS bucket after publishing.
        """
        self.bucket_service.delete_file_from_bucket(schema_file_name)
