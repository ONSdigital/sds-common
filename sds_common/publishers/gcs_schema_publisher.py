import requests
from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.schema.schema import Schema
from sds_common.services.gcp_file_service import GcpFileService
from sds_common.services.sds_request_service import SdsRequestService


class GcsSchemaPublisher(SchemaPublisher):
    """
    Publisher for retrieving and publishing schemas from Google Cloud Storage (GCS) buckets.
    """
    def __init__(self, sds_request_service: SdsRequestService, file_service: GcpFileService):
        super().__init__(sds_request_service)
        self.file_service = file_service

    def _retrieve_schema(self, file_name: str) -> dict:
        """
        Retrieve the schema JSON file from the GCS bucket.

        :param file_name: The name of the schema file to retrieve.
        :return: The schema as a dictionary.
        """
        return self.file_service.retrieve_json_file(file_name)

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

        :param schema_file_name: The name of the schema file to delete.
        """
        self.file_service.delete_file(schema_file_name)
