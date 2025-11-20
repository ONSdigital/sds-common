from abc import ABC, abstractmethod

from sds_common.schema.schema import Schema
from sds_common.services.sds_schema_request_service import SdsSchemaRequestService


class SchemaPublisher(ABC):
    def __init__(self):
        self.schema_request_service = SdsSchemaRequestService()

    @abstractmethod
    def _retrieve_schema(self, file_name: str):
        pass

    def publish(self, file_name: str):
        schema_json = self._retrieve_schema(file_name)
        schema = Schema.set_schema(schema_json, file_name)
        response = self.schema_request_service.post_schema(schema)
        return response
