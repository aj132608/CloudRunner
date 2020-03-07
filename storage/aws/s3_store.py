import logging

import boto3
import os

from awscli.errorhandler import ClientError
from botocore.client import Config


class S3Storage:
    """
    This class implements functionality to communicate with
    AWS S3.
    """

    def __init__(self, credentials_dict):
        """
        The constructor initializes the variables.
        """
        self.credentials_dict = credentials_dict
        self.storage_resource, \
        self.storage_client = self.connect()

    def connect(self):
        """
        Parses the credentials dictionary and populates the following class
        variables:
        :return connection_obj: Boto3 resource object
        """
        access_key = self.credentials_dict['cdsm_storage_access_key']
        secret_key = self.credentials_dict['cdsm_storage_secret_key']
        region = self.credentials_dict['region']
        endpoint_url = self.credentials_dict['endpoint_url']
        connection_resource = boto3.resource('s3',
                                             aws_access_key_id=access_key,
                                             aws_secret_access_key=secret_key,
                                             config=Config(signature_version='s3v4'),
                                             endpoint_url=endpoint_url,
                                             region_name=region)
        connection_client = boto3.client('s3',
                                         aws_access_key_id=access_key,
                                         aws_secret_access_key=secret_key,
                                         config=Config(signature_version='s3v4'),
                                         endpoint_url=endpoint_url,
                                         region_name=region)

        return connection_resource, connection_client

    def reset_connection(self, credentials_dict):
        """
        This function resets the connection to a different
        google account store specified by the credentials_dict.
        :param credentials_dict:
        :returns nothin:
        """
        self.credentials_dict = credentials_dict
        self.storage_resource, \
        self.storage_client = self.connect()

    def get_bucket_object(self, bucket_name):
        """
        Thus function returns a bucket object.
        :param bucket_name: Name of the bucket
        :returns bucket_obj: Bucket Object
        """
        bucket = self.storage_resource.Bucket(bucket_name)
        return bucket

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
        region = self.credentials_dict['region']
        if bucket_name in self.get_buckets(True):
            print(f"Bucket already exists")

            if start_new:
                self.delete_bucket(bucket_name)
                bucket = self.storage_client.create_bucket(Bucket=bucket_name,
                                                           CreateBucketConfiguration={
                                                               'LocationConstraint': region
                                                           })
        else:
            print(f"Creating new bucket")
            try:
                bucket = self.storage_client.create_bucket(Bucket=bucket_name,
                                                           CreateBucketConfiguration={
                                                               'LocationConstraint': region
                                                           })
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
        buckets = self.storage_resource.buckets.all()

        if return_names:
            buckets = [bucket.name for bucket in buckets]

        return buckets

    def persist_file(self, bucket, local_file_path, s3_key=None):
        """
        :param bucket: Name/Instance of the bucket to store into.
        :param s3_key: Path on the bucket
        :param local_file_path: Location of the file.
        :return:
        """
        file = open(local_file_path, 'rb')
        if s3_key is None:
            s3_key = os.path.basename(local_file_path)
        self.storage_client.put_object(Bucket=bucket,
                                       Key=(s3_key), Body=local_file_path)
        file.close()

    def download_file(self, bucket, key, local_storage_path):
        """
        This function downloads a given file to a specified path from
        the buckets root.
        :param local_storage_path: Path to store
        :param key: Path of the file to where to download
        :param bucket: Name/Object of the Bucket to download from.
        :returns nothing:
        """
        with open(local_storage_path, 'wb') as data:
            self.storage_client.download_fileobj(bucket, key, data)

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
        blob_list = bucket_obj.objects.all()

        if return_names:
            blob_list = [blob.key for blob in blob_list]

        return blob_list

    def delete_bucket(self, bucket):
        """
        Takes in a boto3 object and a bucket name. This function deletes the
        bucket's contained files then deletes the bucket itself.
        :param bucket_name: Name of the Bucket
        :return: Nothing
        """
        if isinstance(bucket, str):
            bucket = self.get_bucket_object(bucket)

        # delete all the contained files
        for key in bucket.objects.all():
            key.delete()

        # delete the bucket
        bucket.delete()

# credential = {
#     "region": "us-west-2",
#     "cdsm_storage_access_key": "AKIAWA6NKF4SYIQAN6Q4",
#     "cdsm_storage_secret_key": "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",
#     "endpoint_url": "https://s3-us-west-2.amazonaws.com"
# }
# s3 = S3Storage(credential)
# s3.download_folder("alexjfucker", "hello")
# buckets = s3.get_buckets(True)
# print(buckets)
# s3.create_bucket("alexjfucker")
# print(buckets)
# s3.persist_file("alexjfucker", "hello/why/Cloud Runner.pdf", "./Cloud DSM.pdf")

# r = s3.download_file("alexjfucker", "hello/why/Cloud Runner.pdf", "./CR.pdf")
# print(r.read())
# bucket_obj = s3.get_bucket_object(buckets[-2])
# files = s3.get_files_in_bucket(bucket_obj, True)
#
# s3.download_file(files[0], os.getcwd(), buckets[-2])
