import requests

from sds_common.config.config import CONFIG
from sds_common.models.dataset_models import DatasetMetadata
from sds_common.models.dataset_publish_errors import DatasetMetadataRetrievalError, DatasetCreateError
from sds_common.models.schema_publish_errors import SchemaMetadataError, SchemaPostError
from sds_common.schema.schema import Schema
from sds_common.config.logging_config import logging
from sds_common.services.http_service import HttpService

logger = logging.getLogger(__name__)

class SdsRequestService:
    def __init__(self, http_service: HttpService, sds_url: str):
        self.http_service = http_service
        self.sds_url = sds_url


    def get_schema_metadata(self, survey_id: str) -> requests.Response:
        """
        Call the GET schema_metadata SDS endpoint and return the response.

        :param survey_id: the survey_id of the schema.
        :return: the response from the schema_metadata endpoint.
        :raises SchemaMetadataError: if the response status code is not 200 or 404.
        """
        url = f"{self.sds_url}{CONFIG.GET_SCHEMA_METADATA_ENDPOINT}"
        response = self.http_service.make_get_request(url, params={"survey_id": survey_id})
        # If the response status code is 404, a new survey is being onboarded.
        if response.status_code != 200 and response.status_code != 404:
            raise SchemaMetadataError(survey_id, response.status_code)
        return response

    def get_all_schema_metadata(self) -> requests.Response:
        """
        Call the GET schema_metadata endpoint and return the response.

        :return: the response from the schema_metadata endpoint.
        """
        url = f"{self.sds_url}{CONFIG.GET_ALL_SCHEMA_METADATA_ENDPOINT}"
        response = self.http_service.make_get_request(url)
        if response.status_code != 200:
            raise SchemaMetadataError(response.json(), response.status_code)
        return response

    def post_schema(self, schema: Schema) -> requests.Response:
        """
        Post the schema to SDS.

        :param schema: the schema to be posted.
        :return response: the response from the POST request.
        :raises SchemaPostError: if the response status code is not 200.
        """
        logger.info(f"Posting schema for survey {schema.survey_id}")
        url = f"{self.sds_url}{CONFIG.POST_SCHEMA_ENDPOINT}"
        response = self.http_service.make_post_request(url, schema.json, params={"survey_id": schema.survey_id})
        if response.status_code != 200:
            raise SchemaPostError(schema.filepath, response.status_code)
        else:
            logger.info(
                f"Schema {schema.filepath} posted for survey {schema.survey_id}"
            )
            return response

    def get_dataset_create(self):
        """
        Call the GET dataset/create SDS endpoint to process a new dataset.

        :return: the response from the dataset/create endpoint.
        """
        url = self.sds_url + CONFIG.DATASET_CREATE_PATH
        response = self.http_service.make_get_request(url)
        if response.status_code != 200:
            raise DatasetCreateError(response.status_code)
        return response

    def get_dataset_metadata(self, survey_id: str, period_id: str) -> list[DatasetMetadata]:
        """
        Call the GET dataset_metadata SDS endpoint and return the response.

        :param survey_id: the survey_id of the dataset.
        :param period_id: the period_id of the dataset.
        :return: a list of DatasetMetadata objects.
        """
        url = self.sds_url + CONFIG.GET_DATASET_METADATA_ENDPOINT
        response = self.http_service.make_get_request(url, params={"survey_id": survey_id, "period_id": period_id})
        if response.status_code != 200:
            raise DatasetMetadataRetrievalError(survey_id, period_id, response.status_code)
        return [DatasetMetadata(**dataset) for dataset in response.json()]
