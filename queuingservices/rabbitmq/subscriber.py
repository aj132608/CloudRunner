import pika
import json


class Subscriber:

    """

    This Class will be a worker for a RabbitMQ queuing service. It will be
    responsible for listening for and processing messages as well as executing
    tasks whenever it receives a message.

    """

    def __init__(self, endpoint, queue_name):
        self.worker_busy = False
        self._connection = None
        self._channel = None
        self.queue_name = queue_name
        self.endpoint = endpoint
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

    @staticmethod
    def _callback(ch, method, props, body):

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
            print("Completion was selected!")
        elif message_dict['submission']:
            print("Submission was selected!")

        print(f"Bucket: {message_dict['bucket_name']}")
        print(f"Username: {message_dict['username']}")
        print(f"Project ID: {message_dict['project_id']}")
        print(f"Experiment ID: {message_dict['experiment_id']}")
        print(f"Job ID: {message_dict['job_id']}")

        Subscriber._run_task()

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

    def  start_server(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')

        """

        This function initiates the consumption or listening for messages.

        It will be responsible for the following:

        - creating and starting the consumer

        - assigning the consumer a callback function that will execute every time
        a message is received.

        - closing the connection on ctr+c gracefully

        :return:
        """
        print("Hello from server")
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

    @staticmethod
    def _run_task():
        """
        blank slate function to execute something

        :return:
        """
        from tests.queue_tests.sample_task import SampleTask

        task_obj = SampleTask()

        try:
            number = task_obj.fibonacci(10)

            print(f"fib(10) = {number}")
        except Exception as e:
            print("There was an error in executing the task.")
            print(f"Exception: {e}")
