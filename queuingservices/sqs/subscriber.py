import boto3

from botocore.client import Config


class Subscriber:
    """

    This class is a Worker for the SQS Queuing Service.

    """

    def __init__(self, credentials_dict, queue_url=None):
        self._user_id = None
        self.queue_url = queue_url
        self.credentials_dict = credentials_dict
        self._client_obj = self._connect()

    def _connect(self):

        """

        This function unpacks the credentials from the credentials dictionary
        and creates a client object.

        :return:
        """

        # Unpack the credentials from the dictionary
        access_key = self.credentials_dict['access_key']
        secret_key = self.credentials_dict['secret_key']
        region = self.credentials_dict['region']

        try:
            self.queue_url = self.credentials_dict['queue_url']
        except KeyError:
            # You have no url and probably nothing will happen.
            pass

        client_obj = boto3.client('sqs',
                                  aws_access_key_id=access_key,
                                  aws_secret_access_key=secret_key,
                                  config=Config(signature_version='s3v4'),
                                  region_name=region)

        return client_obj

    def reconnect(self, credentials_dict):

        """

            This public function will take in a new credentials dictionary,
            pass it into the credentials_dict class variable, and call
            _connect() again to retrieve the updated resource and client
            objects

            :param credentials_dict:
            :return: Nothing
        """

        self.credentials_dict = credentials_dict

        self._client_obj = self._connect()

    def _get_user_id(self):

        """

        This function will extract the user id from the queue url and
        return it.

        :return: user id corresponding to the queue url
        """

        if self.queue_url is None:
            return None
        else:
            # Separate the URL into elements previously separated by
            # forward slashes
            url_element_list = self.queue_url.split('/')

            # Get the index of the user id relative to the length of
            # the url element array
            user_id_index = len(url_element_list) - 2

            return url_element_list[user_id_index]

    def _retrieve_messages(self):

        """

        This function will receive a batch of messages from a queue
        specified by the queue url.

        :return: If there are messages, it will return them. Otherwise, it
        will return None.
        """

        response = self._client_obj.receive_message(
            QueueUrl=self.queue_url,
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

        number = Subscriber._run_task()
        print(f"fib(10) = {number}")

    def _delete_message(self, receipt_handle):

        """

        Deletes the message corresponding to the passed in receipt handle

        :param receipt_handle:
        :return:
        """

        self._client_obj.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

    @staticmethod
    def _run_task():

        """

        Generic task that executes whenever a message is received.

        :return:
        """

        from tests.queue_tests.sample_task import SampleTask

        task_obj = SampleTask()

        number = task_obj.fibonacci(10)

        return number

    def start_server(self):
        """

        This function will be responsible for listening for messages and
        handling them appropriately.

        :return:
        """

        print("Waiting for messages...")

        while True:

            try:
                current_message_batch = self._retrieve_messages()

                if current_message_batch is None:
                    pass
                else:
                    self._process_first_message(current_message_batch)

            except KeyboardInterrupt:
                print("Closing Worker")
                break

            except Exception as e:
                print(f"Exception: {e}")
                print("Closing Worker")
                break
