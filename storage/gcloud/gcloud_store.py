import os

from google.cloud import storage


class GCloudStorage:
    """
    This class implements functionality to communicate with
    GCloud Storage.
    """

    def __init__(self, credentials_dict):
        """
        The constructor initializes the variables.
        """
        self.credentials_dict = credentials_dict
        self.storage_client = self.connect()

    def connect(self):
        """
        This function uses the credentials to connect to the Google Store.
        :returns google_storage_connect: A Storage instance connection object
        """
        credentials_path = self.credentials_dict["cdsm_credential_path"]
        google_storage_connect = storage.Client.from_service_account_json(
                                            credentials_path)
        return google_storage_connect

    def get_bucket_object(self, bucket_name):
        """
        Thus function returns a bucket object.
        :param bucket_name: Name of the bucket
        :returns bucket_obj: Bucket Object
        """
        bucket = self.storage_client.get_bucket(bucket_name)
        return bucket

    def reset_connection(self, credential_path):
        """
        This function resets the connection to a different
        google account store specified by the credentials_path.
        :param credential_path:
        :return:
        """
        self.credentials_path = credential_path
        self.storage_client = self.connect()

    def create_bucket(self, bucket_name, start_new=False):
        """
        Thus function creates a new bucket. If the bucket already
        exists it is deleted and then re-instantantiated
        :param start_new: If bucket already exists, the old bucket will be deleted
        if this is set to True and then recreated. If this is set to false, an object
        of the existing bucket will be returned.
        :param bucket_name: Name of the bucket
        :return bucket: Object of that bucket
        """
        if bucket_name in self.get_buckets(True):
            print(f"Bucket already exists")

            if start_new:
                self.delete_bucket(bucket_name)
                bucket = self.storage_client.create_bucket(bucket_name)
        else:
            print(f"Creating new bucket")
            try:
                bucket = self.storage_client.create_bucket(bucket_name)
            except Exception as e:
                print(f"Failed to create bucket: {e}")
                bucket = False

        return bucket

    def get_buckets(self, return_names=True):
        """
        This function returns a list of already existing buckets
        associated with the account
        :param return_names: If this is set to True, the names of the buckets
        will be returned else the bucket instances will be returned.
        :return buckets: List of buckets.
        """
        buckets = self.storage_client.list_buckets()
        if return_names:
            buckets = [bucket.name for bucket in buckets]
        return buckets

    def delete_bucket(self, bucket):
        """
        This function deletes a given bucket.
        :param bucket: Name or instance of the bucket
        :returns nothing:
        """
        try:
            self.storage_client.delete_bucket(bucket)
        except Exception as e:
            print(f"Failed to delete GCloud Bucket, {e}")

    def persist_file(self, file_name, local_file_path, bucket):
        """
        This function stores the given file in an already existing bucket
        :param file_name: Name of the file that needs to be attached while uploading
        :param local_file_path: Location of the file.
        :param bucket: Name/Instance of the bucket to store into.
        :returns nothing:
        """
        bucket_obj = self.get_bucket_object(bucket)
        blob = bucket_obj.blob(file_name)
        try:
            blob.upload_from_filename(local_file_path)
        except Exception as e:
            print(f"File Upload to GCloud failed, {e}")

    def get_files_in_bucket(self, bucket, return_names=False):
        """
        This function returns the names/instances of the files in the
        specified bucket
        :param bucket: Name/Instance of the bucket
        :param return_names: If this is set to True, the names of the files
        will be returned else the bucket instances will be returned.
        :returns blob_list: List of files
        """
        if isinstance(bucket, str):
            bucket_names = self.get_buckets(return_names=True)

            if bucket not in bucket_names:
                raise FileNotFoundError(f"Bucket {bucket} does not Exist")

            bucket_obj = self.get_bucket_object(bucket)
        else:
            bucket_obj = bucket

        # List the blobs in the container
        blob_list = bucket_obj.list_blobs()

        if return_names:
            blob_list = [blob.name for blob in blob_list]

        return blob_list

    def download_file(self, file_name, local_file_path,
                      bucket):
        """
        This function downloads a given file to a specified path from
        the bucket specified.
        :param file_name: Name/Folder/Path of the file to download
        :param local_file_path: Path of the file to where to download
        :param bucket: Name of the Bucket to download from.
        :returns nothing:
        """
        files = self.get_files_in_bucket(bucket, True)
        if file_name not in files:
            raise FileNotFoundError(f"File {file_name} does not "
                                    f"exist in bucket {bucket}")

        bucket_obj = self.get_bucket_object(bucket)
        blob_object = bucket_obj.blob(file_name)

        with open(local_file_path, 'wb') as data:
            blob_object.download_to_file(data)

        # blob_object.download_to_filename(file_path)

#
# creds = {
#         "cdsm_credential_path": "/Users/mo/Desktop/mineai/Cloud Runner Extras/_accesskeys/MineAI-5d1871963a9d.json",
# }
# gcloud_store = GCloudStorage(creds)
# # gcloud_store.create_bucket("bucket-random")
# print(gcloud_store.get_buckets())
# gcloud_store.persist_file("Hello/CR.pdf", "./Cloud DSM.pdf", "bucket-random")






