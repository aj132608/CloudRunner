import pika

from queuingservices.callback import callback_handler


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

    def _process_first_message(self, ch, method, props, body):

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
        callback_handler(body, self.storage_obj)

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
                on_message_callback=self._process_first_message,
                auto_ack=True,
                consumer_tag="current consumer")
            self._channel.start_consuming()

        except KeyboardInterrupt:
            print("Exiting gracefully")
            self._connection.close()


