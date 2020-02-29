import pika

EXCHANGE_TYPE = 'direct'


class QueueLifecycle:

    """

    This function will be responsible for the creation and deletion of queues
    and exchanges using the rabbitmq queuing service.

    """

    def __init__(self, endpoint):
        self.endpoint = endpoint
        connection, channel = self._connect()
        self._connection = connection
        self._channel = channel

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

    def create_and_bind_exchange(self, exchange_name, queue_name):

        """

        This function creates an exchange with a specified name and binds
        it to a specified queuingservices.

        :param exchange_name:
        :param queue_name:
        :return: boolean value indicating whether or not the exchange was
        successfully created and bound.

        """

        global EXCHANGE_TYPE

        try:
            self._channel.exchange_declare(exchange=exchange_name,
                                           exchange_type=EXCHANGE_TYPE)

            self._channel.queue_bind(exchange=exchange_name,
                                     queue=queue_name)

            return True
        except Exception as e:
            print("create_and_bind_exchange() failed.")
            print(f"Exception: {e}")

            return False

    def create_queue(self, queue_name):

        """

        This function will create a queuingservices on the specified channel using the
        name passed in from queue_name.

        :param queue_name:
        :return: boolean value indicating whether or not the queuingservices was
        successfully created.

        """

        try:
            self._channel.queue_declare(queue=queue_name,
                                        durable=True)
            return True
        except Exception as e:
            print(f"The following queuingservices could not be created: {queue_name}")
            print(f"Exception: {e}")

            return False

    def delete_queue(self, queue_name):

        """

        This function will delete a queuingservices on the specified channel using the
        name passed in from queue_name.

        :param queue_name:
        :return: boolean value indicating whether or not the queuingservices was
        successfully created.

        """

        try:
            self._channel.queue_delete(queue=queue_name)

            return True
        except Exception as e:
            print(f"The following queuingservices could not be deleted: {queue_name}")
            print(f"Exception: {e}")

            return False
