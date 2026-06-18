from sds_common.config.config import CONFIG
from sds_common.models.dataset_models import DatasetMetadata
from sds_common.models.dataset_publish_errors import DatasetMetadataRetrievalError, DatasetCreateError
from sds_common.services.http_service import HttpService


class SdsDatasetRequestService:
    def __init__(self):
        self.http_service = HttpService.create(True)

    def get_dataset_create(self):
        """
        Call the GET dataset/create SDS endpoint to process a new dataset.

        :return: the response from the dataset/create endpoint.
        """
        url = CONFIG.SDS_URL + CONFIG.DATASET_CREATE_PATH
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
        url = CONFIG.SDS_URL + CONFIG.GET_DATASET_METADATA_ENDPOINT
        response = self.http_service.make_get_request(url, params={"survey_id": survey_id, "period_id": period_id})
        if response.status_code != 200:
            raise DatasetMetadataRetrievalError(survey_id, period_id, response.status_code)
        return [DatasetMetadata(**dataset) for dataset in response.json()]
