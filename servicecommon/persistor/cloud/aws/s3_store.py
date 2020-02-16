import boto3

from botocore.client import Config
from botocore.client import ClientError
from framework.interfaces.persistence.persistence import Persistence


class S3Store(Persistence):
    def __init__(self, credentials_dict, bucket_name, file_path, file_name, restore_path=None):
        """

        Initialize the following class variables and ensure that restore path
        is properly.

        :param bucket_name:
        :param file_path:
        :param restore_path:
        """
        super().__init__()
        self.credentials_dict = credentials_dict
        self.bucket_name = bucket_name
        self.file_path = file_path
        self.file_name = file_name

        if restore_path is None:
            self.restore_path = self.file_path
        else:
            self.restore_path = restore_path

        self.endpoint_url = None
        self.access_key = None
        self.secret_key = None
        self.region = None

        self.set_credentials()

    def set_credentials(self):
        """

        Parses the credentials dictionary and populates the following class
        variables:

        :return: Nothing
        """
        self.endpoint_url = self.credentials_dict['endpoint_url']
        self.access_key = self.credentials_dict['access_key']
        self.secret_key = self.credentials_dict['secret_key']
        self.region = self.credentials_dict['region']

    def persist(self):
        """

        Utilizes the class variables and uploads the file at 'file_path' to the
        passed in bucket name with the specified file name.

        :return: Nothing
        """

        # create the boto3 client object with the passed in credentials
        s3_obj = boto3.client('s3',
                              endpoint_url=self.endpoint_url,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key,
                              config=Config(signature_version='s3v4'),
                              region_name=self.region)

        # check if the bucket already exists
        bucket_exists = None
        try:
            s3_obj.meta.client.head(Bucket=self.bucket_name)
            bucket_exists = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                bucket_exists = False

        if bucket_exists is None:
            return False

        # if the bucket doesn't exist, create it
        if not bucket_exists:
            self.create_bucket(s3_obj, self.bucket_name)

        # upload the file
        s3_obj.upload_file(self.file_path, self.bucket_name, self.file_name)

    def restore(self):
        """

        This function downloads the specified file from the specified bucket
        to a specific path.

        :return: Nothing
        """

        # create the boto3 client object with the passed in credentials
        s3_obj = boto3.client('s3',
                              endpoint_url=self.endpoint_url,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key,
                              config=Config(signature_version='s3v4'),
                              region_name=self.region)

        # download the file to the restore path
        s3_obj.download_file(self.bucket_name, self.file_name, self.restore_path)

    @staticmethod
    def delete_bucket(s3, bucket_name):
        """

        Takes in a boto3 object and a bucket name. This function deletes the
        bucket's contained files then deletes the bucket itself.

        :param s3:
        :param bucket_name:
        :return: Nothing
        """
        bucket = s3.Bucket(bucket_name)

        # delete all the contained files
        for key in bucket.objects.all():
            key.delete()

        # delete the bucket
        bucket.delete()

    @staticmethod
    def create_bucket(s3, bucket_name):
        s3.create_bucket(Bucket=bucket_name)
