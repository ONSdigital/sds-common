from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.schema.schema import Schema
from sds_common.services.schema_validator_service import SchemaValidatorService
from sds_common.utilities.utils import fetch_raw_schema_from_github


class PubsubSchemaPublisher(SchemaPublisher):
    def __init__(self):
        super().__init__()

    def _retrieve_schema(self, file_name: str):
        return fetch_raw_schema_from_github(file_name)

    def _validate(self, validator: SchemaValidatorService, schema: Schema):
        validator.validate_schema(schema)

    def publish(self, file_name: str):
        schema_json = self._retrieve_schema(file_name)
        schema = Schema.set_schema(schema_json, file_name)
        self._validate(SchemaValidatorService(), schema)
        response = self.schema_request_service.post_schema(schema)
        return response
