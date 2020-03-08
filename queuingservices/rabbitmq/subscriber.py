import pika
import json
import os

from completionservice.completion_storage_interface import CompletionStorageInterface


class Subscriber:

    """

    This Class will be a worker for a RabbitMQ queuing service. It will be
    responsible for listening for and processing messages as well as executing
    tasks whenever it receives a message.

    """

    def __init__(self, endpoint, queue_name, storage_obj=None):
        self.worker_busy = False
        self._connection = None
        self._channel = None
        self.queue_name = queue_name
        self.endpoint = endpoint
        self.storage_obj = storage_obj
        self._connection, self._channel = self._connect()

    def _connect(self):

        """

        This function will connect to the RabbitMQ server and create a
        connection and channel object

        :return: connection and channel objects

        """

        params = pika.URLParameters(self.endpoint)

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        return connection, channel

    def reconnect(self, endpoint):

        """

        This function will accept a new endpoint to connect to and update
        the connection and channel class variables.

        :param endpoint:
        :return: Nothing

        """

        self.endpoint = endpoint

        self._connection, self._channel = self._connect()

    def _callback(self, ch, method, props, body):

        """

        This is the callback function that is called every time a message is
        received.

        It prints out the message body then runs some task.

        New messages are blocked during this procedure.

        :param ch:
        :param method:
        :param props:
        :param body:
        :return:

        """

        print(f" [x] Recieved {body}")

        message_dict = json.loads(body)

        if message_dict['completion']:
            # build the local path to download job data
            local_path = f"{os.getcwd()}/{message_dict['experiment_id']}/{message_dict['job_id']}.tar"

            self.retrieve_job_data(bucket=message_dict['bucket_name'],
                                   username=message_dict['username'],
                                   project_id=message_dict['project_id'],
                                   experiment_id=message_dict['experiment_id'],
                                   job_id=message_dict['job_id'],
                                   local_path=local_path)

        elif message_dict['submission']:
            print("Submission was selected!")

        print(f"Bucket: {message_dict['bucket_name']}")
        print(f"Username: {message_dict['username']}")
        print(f"Project ID: {message_dict['project_id']}")
        print(f"Experiment ID: {message_dict['experiment_id']}")
        print(f"Job ID: {message_dict['job_id']}")

        print(" [x] Done")

    def _stop_consuming(self):

        """

        Cancels the consumer on this channel so it won't accept any messages

        :return:
        """

        self._channel.basic_cancel(
            queue=self.queue_name, callback=self._worker_busy_callback)

    def _worker_busy_callback(self):

        """

        Sets the worker_busy variable to True because the worker is currently
        processing a message.

        :return:
        """

        self.worker_busy = True

    def start_server(self):

        """

        This function initiates the consumption or listening for messages.

        It will be responsible for the following:

        - creating and starting the consumer

        - assigning the consumer a callback function that will execute every time
        a message is received.

        - closing the connection on ctr+c gracefully

        :return:
        """
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self._channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._callback,
                auto_ack=True,
                consumer_tag="current consumer")
            self._channel.start_consuming()

        except KeyboardInterrupt:
            print("Exiting gracefully")
            self._connection.close()

    def retrieve_job_data(self, bucket, username, project_id,
                          experiment_id, job_id, local_path):
        """

        This function will download a job file to a specified location with
        a specified file name locally.

        :param bucket:
        :param username:
        :param project_id:
        :param experiment_id:
        :param job_id:
        :param local_path:
        :return:
        """
        storage_master_obj = CompletionStorageInterface(storage_obj=
                                                        self.storage_obj)

        if local_path is None:
            local_path = f"{job_id}.tar"

        storage_master_obj.get_job_data(bucket=bucket,
                                        username=username,
                                        project_id=project_id,
                                        experiment_id=experiment_id,
                                        job_id=job_id,
                                        local_path=local_path)
