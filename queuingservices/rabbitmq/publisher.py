import pika


class Publisher:

    """

    This class will act as a publisher to RabbitMQ Workers or Subscribers and
    it will send messages to them.

    """

    def __init__(self, endpoint):
        self._connection = None
        self._channel = None
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

    def send_message(self, message, queue_name, exchange_name):

        """

        This function will send a specified message to a queuingservices and
        close the connection right after.

        :param exchange_name:
        :param queue_name:
        :param message:
        :return:
        """

        if self._channel.is_closed:
            self._connect()

        try:
            self._channel.basic_publish(
                exchange=exchange_name,
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

            print(f" [x] Sent {message}")
            return True
        except Exception as e:
            print("Message failed to send.")
            print(f"Exception: {e}")
            return False
