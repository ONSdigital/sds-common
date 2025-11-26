from sds_common.enums.buckets import Bucket
from sds_common.repositories.bucket_loader import BucketLoader
from sds_common.repositories.bucket_repository import BucketRepository


class BucketService:
    def __init__(self, bucket: Bucket, loader: BucketLoader, repository_cls=BucketRepository):
        self.bucket = loader.fetch_bucket(bucket)
        self.bucket_repository = repository_cls(self.bucket)

    def upload_file_to_bucket(self, filepath: str):
        """
        Uploads a file to the associated bucket.

        :param filepath: Path to the file to be uploaded.
        """
        self.bucket_repository.upload_file_from_path(filepath)

    def retrieve_json_file_from_bucket(self, filename: str) -> dict:
        """
        Retrieves a JSON file from the associated bucket.

        :param filename: Name of the file to be retrieved.
        :return: The file loaded as a JSON dictionary.
        """
        return self.bucket_repository.get_file_as_json(filename)

    def delete_file_from_bucket(self, filename: str):
        """
        Deletes a file from the associated bucket.

        :param filename: Name of the file to be deleted.
        """
        self.bucket_repository.delete_file(filename)
