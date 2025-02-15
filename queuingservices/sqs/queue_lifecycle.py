import boto3

from botocore.client import Config


class QueueLifecycle:
    """

        This class will be responsible for creating and deleting
        SQS queues.

    """

    def __init__(self, credentials_dict):
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

        self._resource_obj, self._client_obj = self._connect()

    def delete_queue(self, queue_input):

        """

        This function will delete a queue based on the queue_url provided.

        :return: Nothing

        """

        if isinstance(queue_input, str):
            # queue input is a queue url.
            queue_url = queue_input
        else:
            # queue input is a queue object
            queue_url = queue_input.url

        try:
            self._client_obj.delete_queue(
                QueueUrl=queue_url
            )
            return True
        except Exception as e:
            print(f"Exception: {e}")
            return False

    def create_queue(self, queue_name):

        """

        This function will create a queue with the name provided by queue_name.

        :param queue_name:String - must contain only alphanumeric characters,
        punctuation, and end with the .fifo extension.
        :return: Nothing
        """

        try:
            queue = self._resource_obj.create_queue(QueueName=queue_name,
                                                    Attributes={
                                                        'FifoQueue': 'true'
                                                    })
            return queue
        except Exception as e:
            print(f"Exception: {e}")
            return None

