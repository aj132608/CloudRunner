import boto3

from botocore.client import Config


class SQSWorker:
    """

    This class is a Worker for the SQS Queuing Service.

    """
    def __init__(self, credentials_path, queue_url=None):
        self._client_obj = None
        # self._queue = None
        self._access_key = None
        self._secret_key = None
        self._region = None
        self._user_id = None
        self._queue_url = queue_url
        self._credentials_path = credentials_path
        self._get_credentials()

    def _get_credentials(self):

        """

        This function gets all necessary credentials from the credentials.json
        and populates the credentials class variables.

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

        # Check if you still need a queue url
        if self._queue_url is None:
            try:
                # if you do, look for it in the credentials.json file
                self._queue_url = credentials['queue_url']

            except KeyError:
                # if it isn't there either then you can't really do anything
                pass

        # Check the credentials.json for a user_id
        try:
            self._user_id = credentials['user_id']
        except KeyError:
            # retrieve the user id from the queue url
            self._user_id = self._get_user_id()

    def _get_user_id(self):

        """

        This function will extract the user id from the queue url and
        return it.

        :return: user id corresponding to the queue url
        """

        if self._queue_url is None:
            return None
        else:
            # Separate the URL into elements previously separated by
            # forward slashes
            url_element_list = self._queue_url.split('/')

            # Get the index of the user id relative to the length of
            # the url element array
            user_id_index = len(url_element_list) - 2

            return url_element_list[user_id_index]

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

    def _retrieve_messages(self):

        """

        This function will receive a batch of messages from a queue
        specified by the queue url.

        :return: If there are messages, it will return them. Otherwise, it
        will return None.
        """

        self._initialize_client_object()

        response = self._client_obj.receive_message(
            QueueUrl=self._queue_url,
            WaitTimeSeconds=0
        )

        metadata = response['ResponseMetadata']

        if metadata['HTTPStatusCode'] == 200:
            try:
                messages = response['Messages']

                return messages

            except KeyError:
                # print("No messages at this time.")
                return None
        else:
            print("HTTP Error")
            print(f"Status Code: {metadata['HTTPStatusCode']}")
            return None

    def _process_first_message(self, messages):

        """

        This function will take in a list of messages from the retrieved batch
        of messages and process the first one.

        It will execute the following commands:

        1. print the message contents
        2. retrieve the messages unique receipt handle
        3. delete the message
        4. run some generic task

        :param messages:list - list of the message objects
        :return:
        """

        current_message = messages[0]

        print(f"message: {current_message['Body']}")

        receipt_handle = current_message['ReceiptHandle']

        self._delete_message(receipt_handle=receipt_handle)

        number = SQSWorker.run_task()
        print(f"fib(10) = {number}")

    def _delete_message(self, receipt_handle):

        """

        Deletes the message corresponding to the passed in receipt handle

        :param receipt_handle:
        :return:
        """

        self._client_obj.delete_message(
            QueueUrl=self._queue_url,
            ReceiptHandle=receipt_handle
        )

    @staticmethod
    def run_task():

        """

        Generic task that executes whenever a message is recieved.

        :return:
        """

        from tests.queue_tests.sample_task import SampleTask

        task_obj = SampleTask()

        number = task_obj.fibonacci(10)

        return number

    def start_server(self):
        """

        This function will be called initially and will execute all of the
        relevant

        1. Create client object
        4. Check for messages

        :return:
        """

        while True:

            try:
                current_message_batch = self._retrieve_messages()

                if current_message_batch is None:
                    pass
                else:
                    self._process_first_message(current_message_batch)

            except KeyboardInterrupt:
                break
