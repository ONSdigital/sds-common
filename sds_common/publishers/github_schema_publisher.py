import requests

from sds_common.publishers.schema_publisher import SchemaPublisher
from sds_common.schema.schema import Schema
from sds_common.services.http_service import HttpService
from sds_common.services.schema_validator_service import SchemaValidatorService
from sds_common.services.sds_schema_request_service import SdsSchemaRequestService
from sds_common.utilities.utils import fetch_raw_schema_from_github


class GithubSchemaPublisher(SchemaPublisher):
    """
    Publisher class to publish schemas retrieved from a GitHub repository.
    """

    def __init__(
        self,
        schema_request_service: SdsSchemaRequestService,
        validator_service: SchemaValidatorService,
        github_schema_url: str,
        http_service: HttpService,
    ) -> None:
        super().__init__(schema_request_service)
        self.validator = validator_service
        self.github_schema_url = github_schema_url
        self.http_service = http_service

    def _retrieve_schema(self, file_name: str) -> dict:
        """
        Retrieves the schema JSON from a GitHub repository.

        :param file_name: The name of the schema file to retrieve.
        :return: The schema JSON as a dictionary.
        """
        return fetch_raw_schema_from_github(file_name, self.http_service, self.github_schema_url)

    def publish_schema(self, file_name: str) -> requests.Response:
        """
        Publishes the schema to the schema registry after retrieving and validating it.

        :param file_name: The name of the schema file to publish.
        :return: The response from SDS.
        """
        schema_json = self._retrieve_schema(file_name)
        schema = Schema.set_schema(schema_json, file_name)
        self._validate(schema)
        return self.schema_request_service.post_schema(schema)

    def _validate(self, schema: Schema):
        """
        Validates the schema.

        :param schema: The Schema object to validate.
        """
        self.validator.validate_schema(schema)
