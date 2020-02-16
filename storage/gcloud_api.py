from google.cloud import storage
from framework.interfaces.persistence.persistence import Persistence


class GCloudApi(Persistence):
    def __init__(self, credentials_path):

        self.instance = storage.Client.from_service_account_json(
                                                credentials_path)

    def create_bucket(self, bucket_name):

        self.instance.create_bucket(bucket_name)

    def persist(self, bucket_name, tar_path):

        bucket = self.instance.get_bucket(bucket_name)
        blob = bucket.blob(tar_path)
        blob.upload_from_filename(tar_path)

    def restore(self, bucket_name, tar_path):

        bucket = self.instance.get_bucket(bucket_name)
        blob = bucket.blob(tar_path)
        blob.download_to_filename(tar_path)





