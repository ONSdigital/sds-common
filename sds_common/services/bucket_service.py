

class BucketService:
    def __init__(self, bucket_repository):
        self.bucket_repository = bucket_repository

    def create_bucket(self, name, region):
        return self.bucket_repository.create(name, region)

    def delete_bucket(self, bucket_id):
        return self.bucket_repository.delete(bucket_id)

    def list_buckets(self):
        return self.bucket_repository.list_all()

    def get_bucket(self, bucket_id):
        return self.bucket_repository.get(bucket_id)
    def retrieve_file(self, bucket_id, file_name):
        return self.bucket_repository.retrieve_file(bucket_id, file_name)
