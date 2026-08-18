from __future__ import annotations
from sds_common.config.config import Config, get_config
import logging
from sds_common.models.dataset_models import DatasetMetadata
from sds_common.models.dataset_publish_errors import DatasetMetadataRetrievalError
from sds_common.services.http_service import HttpService

logger = logging.getLogger(__name__)


class SdsDatasetRequestService:
    def __init__(self, http_service: HttpService, config: Config | None = None) -> None:
        self.http_service = http_service
        self.config = config or get_config()

    def get_metadata(self, survey_id: str, period_id: str) -> list[DatasetMetadata] | None:
        """
        Call the GET /datasets/metadata SDS endpoint and return the response.

        :param survey_id: the survey_id of the dataset.
        :param period_id: the period_id of the dataset.
        :return: a list of DatasetMetadata objects, or ``None`` if no datasets exist (404).
        :raises DatasetMetadataRetrievalError: if the response status code is not 200 or 404.
        """
        url = self.config.SDS_URL + self.config.GET_DATASET_METADATA_ENDPOINT
        response = self.http_service.make_get_request(url, params={'survey_id': survey_id, 'period_id': period_id})
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            logger.warning(
                "Failed to fetch dataset metadata for survey '%s', period '%s'. Status: %d",
                survey_id, period_id, response.status_code,
            )
            raise DatasetMetadataRetrievalError(survey_id, period_id, response.status_code)
        return [DatasetMetadata(**dataset) for dataset in response.json()]
