import boto3

from botocore.client import Config


class SQSQueue:
    """

        This class will be responsible for creating and deleting
        SQS queues.

        """

    def __init__(self, credentials_path):
        self._resource_obj = None
        self._client_obj = None
        self._queue = None
        self._access_key = None
        self._secret_key = None
        self._region = None
        self._credentials_path = credentials_path
        self._get_credentials()

    def _get_credentials(self):

        """

            Grabs the credentials for the authorized AWS user from a json file
            titled 'credentials.json' from the path specified in the constructor.

            It uses the JsonPersistor class from the persistor utilities to
            convert the credentials json file over to a dictionary.

            Once converted, the function extracts the credentials and populates
            the following class variables:

            - access_key
            - secret_key
            - region

            :return: Nothing

        """

        from servicecommon.persistor.local.json.json_persistor import JsonPersistor

        json_restorer = JsonPersistor(dict=None,
                                      base_file_name="credentials",
                                      folder=self._credentials_path)

        credentials = json_restorer.restore()

        self._access_key = credentials['access_key']
        self._secret_key = credentials['secret_key']
        self._region = credentials['region']

    def _initialize_resource_object(self):

        """

        Creates the boto3 resource object with the passed in credentials

        :return: Nothing

        """

        self._resource_obj = boto3.resource('sqs',
                                            aws_access_key_id=self._access_key,
                                            aws_secret_access_key=self._secret_key,
                                            config=Config(signature_version='s3v4'),
                                            region_name=self._region)

    def _initialize_client_object(self):

        """

        Creates the boto3 client object with the passed in credentials

        :return: Nothing

        """

        self._client_obj = boto3.client('sqs',
                                        aws_access_key_id=self._access_key,
                                        aws_secret_access_key=self._secret_key,
                                        config=Config(signature_version='s3v4'),
                                        region_name=self._region)

    def get_queue_url(self):

        """

        This function will return the queue url if the queue object has been
        populated.

        Otherwise, it will return None.

        :return: queue url or None
        """

        if self._queue is None:
            return None
        else:
            return self._queue.url

    def delete_queue(self):

        """

        This function will delete a queue based on the queue_url provided.

        :return: Nothing
        """

        self._initialize_client_object()

        try:
            self._client_obj.delete_queue(
                QueueUrl=self.get_queue_url()
            )
        except Exception as e:
            print(f"Exception: {e}")

    def create_queue(self, queue_name):

        """

        This function will create a queue with the name provided by queue_name.

        :param queue_name:String - must contain only alphanumeric characters,
        punctuation, and end with the .fifo extension.
        :return: Nothing
        """

        self._initialize_resource_object()

        try:
            self._queue = self._resource_obj.create_queue(QueueName=queue_name,
                                                          Attributes={
                                                              'FifoQueue': 'true'
                                                          })
        except Exception as e:
            print(f"Exception: {e}")

