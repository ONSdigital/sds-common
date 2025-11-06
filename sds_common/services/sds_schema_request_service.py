import requests
from sds_common.config.logging_config import logging
from sds_common.config.config import CONFIG
from sds_common.models.schema_publish_errors import (
    SchemaMetadataError,
    SchemaPostError,
)
from sds_common.schema.schema import Schema
from sds_common.services.http_service import HttpService
from sds_common.utilities.utils import generate_sds_headers

logger = logging.getLogger(__name__)


class SdsSchemaRequestService:
    """
    Service to handle requests to SDS schema endpoints.
    """
    def __init__(self):
        self.http_service = HttpService.create(generate_sds_headers())

    def get_schema_metadata(self, survey_id: str) -> requests.Response:
        """
        Call the GET schema_metadata SDS endpoint and return the response.

        Parameters:
            survey_id (str): the survey_id of the schema.

        Returns:
            requests.Response: the response from the schema_metadata endpoint.
        """
        url = f"{CONFIG.SDS_URL}{CONFIG.GET_SCHEMA_METADATA_ENDPOINT}{survey_id}"
        response = self.http_service.make_get_request(url)
        # If the response status code is 404, a new survey is being onboarded.
        if response.status_code != 200 and response.status_code != 404:
            raise SchemaMetadataError(survey_id, response.status_code)
        return response

    def post_schema(self, schema: Schema) -> None:
        """
        Post the schema to SDS.

        Parameters:
            schema (Schema): the schema to be posted.
        """
        logger.info(f"Posting schema for survey {schema.survey_id}")
        url = f"{CONFIG.SDS_URL}{CONFIG.POST_SCHEMA_ENDPOINT}{schema.survey_id}"
        response = self.http_service.make_post_request(url, schema.json)
        if response.status_code != 200:
            raise SchemaPostError(schema.filepath, response.status_code)
        else:
            logger.info(
                f"Schema {schema.filepath} posted for survey {schema.survey_id}"
            )


SDS_SCHEMA_REQUEST_SERVICE = SdsSchemaRequestService()
