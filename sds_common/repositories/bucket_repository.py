import json
import os

from google.cloud import storage
from sds_common.config.logging_config import logging

logger = logging.getLogger(__name__)


class BucketRepository:
    def __init__(self, bucket: storage.Bucket):
        self.bucket = bucket

    def get_file_as_json(self, filename: str) -> dict:
        """
        Gets a file from a Google Cloud Bucket with a specific filename and loads it as json.

        :param filename: name of file being loaded.
        :return: dict: the file loaded as json.
        """
        return json.loads(self.bucket.blob(filename).download_as_string())

    def upload_file_from_path(self, filepath: str):
        """
        Uploads a file to the bucket from a local file path.

        :param filepath: path to the local file to be uploaded.
        """
        filename = os.path.basename(filepath)
        blob = self.bucket.blob(filename)
        blob.upload_from_filename(filepath)

    def delete_file(self, filename: str):
        """
        Deletes a file from the bucket with the specified filename.

        :param filename: name of the file to be deleted.
        """
        blob = self.bucket.blob(filename)
        blob.delete()
