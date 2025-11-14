import json

from google.cloud import storage


class BucketRepository:
    def __init__(self, bucket: storage.Bucket):
        self.bucket = bucket

    def get_file_as_json(self, filename: str):
        return json.loads(self.bucket.blob(filename).download_as_string())

    def upload_file_from_path(self, filepath: str):
        blob = self.bucket.blob(filepath)
        blob.upload_from_filename(filepath)
