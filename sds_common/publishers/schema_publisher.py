import requests

from abc import ABC, abstractmethod

from sds_common.services.sds_schema_request_service import SdsSchemaRequestService


class SchemaPublisher(ABC):
    """
    Abstract base class for schema publishers.
    """

    def __init__(self, schema_request_service: SdsSchemaRequestService) -> None:
        self.schema_request_service = schema_request_service

    @abstractmethod
    def _retrieve_schema(self, file_name: str) -> dict:
        """
        Retrieves the schema for the given file name.

        :param file_name: The name of the schema file to be retrieved.
        :return: The schema as a dictionary.
        """
        ...  # pragma: no cover

    @abstractmethod
    def publish_schema(self, file_name: str) -> requests.Response:
        """
        Publishes the schema for the given file name.

        :param file_name: The name of the schema file to be published.
        :return: The response from the schema publishing service.
        """
        ...  # pragma: no cover
