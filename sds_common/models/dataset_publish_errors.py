

class DatasetPublishError(Exception):
    pass


class DatasetMetadataRetrievalError(DatasetPublishError):
    def __init__(self, survey_id: str, period_id: str, status_code: int):
        self.message = f"Failed to retrieve metadata for dataset with survey_id: {survey_id} and period_id: {period_id}, Status code: {status_code}"
        super().__init__(self.message)


class DatasetCreateError(DatasetPublishError):
    def __init__(self, status_code: int):
        self.message = f"Failed to call the dataset/create endpoint. Status code: {status_code}"
        super().__init__(self.message)
