from abc import ABC, abstractmethod

from sds_common.services.sds_schema_request_service import SdsSchemaRequestService


class SchemaPublisher(ABC):
    """
    Abstract base class for schema publishers.
    """
    def __init__(self):
        self.schema_request_service = SdsSchemaRequestService()

    @abstractmethod
    def _retrieve_schema(self, file_name: str):
        """
        Retrieves the schema for the given file name.

        :param file_name: The name of the schema file to be retrieved.
        """
        pass

    @abstractmethod
    def publish_schema(self, file_name: str):
        """
        Publishes the schema for the given file name.

        :param file_name: The name of the schema file to be published.
        """
        pass
