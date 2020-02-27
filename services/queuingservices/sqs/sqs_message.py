import boto3

from botocore.client import Config


class SQSMessage:
    """

    This class will be responsible for sending messages to SQS queues

    """

    def __init__(self, credentials_path):
        self._client_obj = None
        self._queue_url = None
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

        :return:
        """
        from servicecommon.persistor.local.json.json_persistor import JsonPersistor

        json_restorer = JsonPersistor(dict=None,
                                      base_file_name="credentials",
                                      folder=self._credentials_path)

        credentials = json_restorer.restore()

        self._access_key = credentials['access_key']
        self._secret_key = credentials['secret_key']
        self._region = credentials['region']

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

    def get_client_object(self):
        if self._client_obj is None:
            self._initialize_client_object()

        return self._client_obj

    def send_message(self, message, attributes, queue_url, task_id):

        """

        This is the function that will be called externally to actually
        send messages to a queue given a queue url.

        :param task_id:String - The unique id for this particular task

        Example:
        task_id = 'Alex12345'

        :param message:String - The message that will be sent to the queue

        Example:
        message = 'Information about current NY Times fiction bestseller for
        week of 12/11/2016.'

        :param attributes:dict - A dictionary of attributes to describe the
        message being sent.

        Example:
        attributes = {
            'Title': {
                'DataType': 'String',
                'StringValue': 'The Whistler'
            },
            'Author': {
                'DataType': 'String',
                'StringValue': 'John Grisham'
            },
            'WeeksOn': {
                'DataType': 'Number',
                'StringValue': '6'
            }
        }

        :param queue_url:String - url pointing to the desired queue

        Example:
        queue_url = "https://region.queue.amazonaws.com/user_id/queue_name"

        :return: Nothing
        """
        if self._client_obj is None:
            self._initialize_client_object()

        try:
            message_response = self._client_obj.send_message(
                QueueUrl=queue_url,
                DelaySeconds=0,
                MessageAttributes=attributes,
                MessageBody=message,
                MessageGroupId=task_id,
                MessageDeduplicationId=task_id
            )
            print("Message was successfully sent.")
        except Exception as e:
            print("Message Sending was Unsuccessful.")
            print(f"Exception: {e}")
