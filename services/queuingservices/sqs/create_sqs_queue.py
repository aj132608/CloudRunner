import boto3

from botocore.client import Config


class SQSQueue:
    """

        This class will be responsible for creating and deleting
        SQS queues.

    """

    def __init__(self, credentials_dict):
        self._queue = None
        self.credentials_dict = credentials_dict
        (resource_obj, client_obj) = self._connect()
        self._resource_obj = resource_obj
        self._client_obj = client_obj

    def _connect(self):

        """

        This function unpacks the credentials from the credentials dictionary
        and creates a resource and client object.

        :return:
        """

        # Unpack the credentials from the dictionary
        access_key = self.credentials_dict['access_key']
        secret_key = self.credentials_dict['secret_key']
        region = self.credentials_dict['region']

        resource_obj = boto3.resource('sqs',
                                      aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key,
                                      config=Config(signature_version='s3v4'),
                                      region_name=region)

        client_obj = boto3.client('sqs',
                                  aws_access_key_id=access_key,
                                  aws_secret_access_key=secret_key,
                                  config=Config(signature_version='s3v4'),
                                  region_name=region)

        return resource_obj, client_obj

    def reset_connection(self, credential_dict):
        self.credentials_dict = credential_dict

        (self._resource_obj, self._client_obj) = self._connect()

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

    def get_queue(self):
        return self._queue

    def delete_queue(self):

        """

        This function will delete a queue based on the queue_url provided.

        :return: Nothing
        """

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

        try:
            self._queue = self._resource_obj.create_queue(QueueName=queue_name,
                                                          Attributes={
                                                              'FifoQueue': 'true'
                                                          })
            return self._queue
        except Exception as e:
            print(f"Exception: {e}")
            return None
