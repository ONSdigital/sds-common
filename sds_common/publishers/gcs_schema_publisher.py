import requests

from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.schema.schema import Schema
from sds_common.services.file_service import FileService
from sds_common.services.sds_schema_request_service import SdsSchemaRequestService


class GcsSchemaPublisher(SchemaPublisher):
    """
    Publisher for retrieving and publishing schemas from Google Cloud Storage (GCS) buckets.
    """

    def __init__(self, schema_request_service: SdsSchemaRequestService, file_service: FileService) -> None:
        super().__init__(schema_request_service)
        self.bucket_service = file_service

    def _retrieve_schema(self, file_name: str) -> dict:
        """
        Retrieve the schema JSON file from the GCS bucket.

        :param file_name: The name of the schema file to retrieve.
        :return: The schema as a dictionary.
        """
        return self.bucket_service.get_json(file_name)

    def publish(self, file_name: str) -> requests.Response:
        """
        Publish the schema retrieved from the GCS bucket.

        :param file_name: The name of the schema file to publish.
        :return: The response from the schema publishing service.
        """
        schema_json = self._retrieve_schema(file_name)
        schema = Schema.set_schema(schema_json, file_name)
        return self.schema_request_service.publish(schema)

    def cleanup(self, schema_file_name: str) -> None:
        """
        Clean up the schema file from the GCS bucket after publishing.

        :param schema_file_name: The name of the schema file to delete.
        """
        self.bucket_service.delete(schema_file_name)
