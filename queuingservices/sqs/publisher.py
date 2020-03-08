import boto3
import json

from botocore.client import Config


class Publisher:
    """

    This class will be responsible for sending messages to SQS queues

    """

    def __init__(self, credentials_dict):
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

    def get_client_object(self):

        """

        This function is a getter for the protected client object
        class variable.

        :return:
        """

        return self._client_obj

    def send_message(self, message, queue_url, task_id):

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

        :param queue_url:String - url pointing to the desired queue

        Example:
        queue_url = "https://region.queue.amazonaws.com/user_id/queue_name"

        :return: Nothing
        """

        string_message = json.dumps(message)

        try:
            message_response = self._client_obj.send_message(
                QueueUrl=queue_url,
                DelaySeconds=0,
                MessageBody=string_message,
                MessageGroupId=task_id,
                MessageDeduplicationId=task_id
            )
            print("Message was successfully sent.")
            return message_response
        except Exception as e:
            print("Message Sending was Unsuccessful.")
            print(f"Exception: {e}")
            return None
