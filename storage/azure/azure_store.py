import os
from azure.storage.blob import BlobServiceClient

class AzureStorage:
    """
    This class implements the functionality
    to persist and restore files in the Azure
    blobstore.
    """

    def __init__(self, credentials_dict):
        """
        The constructor initializes the variables.
        """
        self.credentials_dict = credentials_dict
        self.blob_service_client = self.connect()

    def connect(self):
        """
        This function uses the credentials to connect to the Azure Store.
        :returns: A BlobServiceClient connection object
        """
        connection_string = self.credentials_dict.get("cdsm_azure"
                                                      "_connection_string")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        return blob_service_client

    def reset_connection(self, credentials_dict):
        """
        This function resets the connection to a different
        google account store specified by the credentials_path.
        :param credential_path:
        :return:
        """
        self.credentials_dict = credentials_dict
        self.blob_service_client = self.connect()

    def get_bucket_object(self, bucket_name):
        """
        Thus function returns a bucket object.
        :param bucket_name: Name of the bucket
        :returns bucket_obj: Bucket Object
        """
        bucket_obj = self.blob_service_client.get_container_client(bucket_name)
        return bucket_obj

    def delete_bucket(self, bucket):
        """
        This function deletes a given bucket.
        :param bucket: Name or instance of the bucket
        :returns nothing:
        """
        try:
            self.blob_service_client.delete_container(bucket,
                                                      lease=None)
        except Exception as e:
            print(f"Failed to delete Azure Bucket, {e}")

    def create_bucket(self, bucket_name, start_new=False):
        """
        Thus function creates a new bucket. If the bucket already
        exists it is deleted and then re-instantantiated
        :param start_new: If bucket already exists, the old bucket will be deleted
        if this is set to True and then recreated. If this is set to false, an object
        of the existing bucket will be returned.
        :param bucket_name: Name of the bucket
        :return:
        """
        try:
            container_client = self.blob_service_client.create_container(bucket_name)
        except:
            print("Bucket already Exists")

            if start_new:
                self.delete_bucket(bucket_name)
                container_client = self.blob_service_client.create_container(bucket_name)
            else:
                container_client = self.get_bucket_object(bucket_name)

        return container_client

    def delete_file_in_bucket(self, file_name, bucket_name):
        """
        This function deletes a given file in the bucket
        :param file_name: Name of the file/blob to be deleted
        :param bucket_name: Name of the bucket do delete from
        :returns nothing:
        """
        bucket_object = self.get_bucket_object(bucket_name)
        try:
            bucket_object.delete_blob(file_name)
        except Exception as e:
            print(f"Azure File Deletion Failed. {e}")

    def get_buckets(self, name_starts_with=None, return_names=True):
        """
        This function returns a list of already existing buckets/containers
        associated with the account
        :param name_starts_with: A filter
        :param return_names: If this is set to True, the names of the buckets
        will be returned else the bucket instances will be returned.
        :return buckets: List of buckets.
        """
        buckets = self.blob_service_client.list_containers(
            name_starts_with=name_starts_with)
        if return_names:
            buckets = [bucket.name for bucket in buckets]
        return buckets

    def persist_file(self, file_name, local_file_path, bucket):
        """
        This function stores the given file in an already existing bucket/container
        :param file_name: Name of the file that needs to be attached while uploading
        :param local_file_path: Location of the file. 
        :param bucket: Name/Instance of the bucket to store into.
        :returns nothing:
        """
        blob_client = self.blob_service_client.get_blob_client(container=bucket,
                                                               blob=file_name)

        try:
            # Upload the created file
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data)
        except Exception as e:
            print(f"File Upload to Azure failed, {e}")

    def get_files_in_bucket(self, bucket_name, return_names=False):
        """
        This function returns the names/instances of the files in the
        specified bucket
        :param bucket_name: Name of the bucket
        :param return_names: If this is set to True, the names of the files
        will be returned else the bucket instances will be returned.
        :returns blob_list: List of files
        """
        bucket_names = self.get_buckets(return_names=True)

        if not bucket_name in bucket_names:
            raise FileNotFoundError(f"Bucket {bucket_name} does not Exist")

        bucket_obj = self.get_bucket_object(bucket_name)

        # List the blobs in the container
        blob_list = bucket_obj.list_blobs()

        if return_names:
            blob_list = [blob.name for blob in blob_list]

        return blob_list

    def download_file(self, file_name, file_path,
                      bucket_name):
        """
        This function downloads a given file to a specified path from
        the bucket specified.
        :param file_name: Name of the file to download
        :param file_path: Path of the file to where to download
        :param bucket_name: Name of the Bucket to download from.
        :returns nothing:
        """
        files = [file.name for file in self.get_files_in_bucket(bucket_name)]
        if not file_name in files:
            raise FileNotFoundError(f"File {file_name} does not "
                                    f"exist in bucket {bucket_name}")

        file_path = os.path.join(file_path, file_name)

        blob_object = self.blob_service_client.get_blob_client(bucket_name, file_name)

        with open(file_path, "wb") as download_file:
            download_file.write(blob_object.download_blob().readall())


# TEST
# cred_dict = {
#     "cdsm_azure_blobstore_connection_string": "DefaultEndpointsProtocol=https;AccountName=mineai;AccountKey=MOJP"
#                                               "pUv2n4zs+zEi9dFVEZNfvMjzj0zgZntiMkUtybok25eAYHxVuU6idwMeS0B0BKXoxGkVAuw5uvlwZ10YZg==;EndpointSuffix=core.windows.net"
# }
# az = AzureStore(cred_dict)
# az.download_file("quickstart0.txt", ".", "quickstart0")