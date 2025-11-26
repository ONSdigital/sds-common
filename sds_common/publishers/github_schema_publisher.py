from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.schema.schema import Schema
from sds_common.services.schema_validator_service import SchemaValidatorService
from sds_common.utilities.utils import fetch_raw_schema_from_github


class GithubSchemaPublisher(SchemaPublisher):
    """
    Publisher class to publish schemas retrieved from a GitHub repository.
    """
    def __init__(self):
        super().__init__()
        self.validator = SchemaValidatorService()

    def _retrieve_schema(self, file_name: str):
        """
        Retrieves the schema JSON from a GitHub repository.

        :param file_name: The name of the schema file to retrieve.
        :return: The schema JSON as a dictionary.
        """
        return fetch_raw_schema_from_github(file_name)

    def publish_schema(self, file_name: str):
        """
        Publishes the schema to the schema registry after retrieving and validating it.

        :param file_name: The name of the schema file to publish.
        :return: The response from SDS.
        """
        schema_json = self._retrieve_schema(file_name)
        schema = Schema.set_schema(schema_json, file_name)
        self._validate(schema)
        response = self.schema_request_service.post_schema(schema)
        return response

    def _validate(self, schema: Schema):
        """
        Validates the schema.

        :param schema: The Schema object to validate.
        """
        self.validator.validate_schema(schema)
