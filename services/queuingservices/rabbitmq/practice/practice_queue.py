import pika


class PracticeQueue:
    def __init__(self):
        self.connection = None
        self.channel = None

    def establish_connection(self, endpoint):
        """

        Take in an endpoint and establish a connection with the queue at that
        endpoint.

        :param endpoint: endpoint of the queue container
        :return: Nothing
        """

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(endpoint))
        self.channel = self.connection.channel()

    def create_sample_queue(self, queue_name):
        """

        Declares a queue on the previously established channel and names it
        whatever is passed in.

        :param queue_name: user specified name for the queue
        :return: Nothing
        """
        self.channel.queue_declare(queue=queue_name, durable=True)

    def create_sample_message(self, queue_name, message):
        """

        Posts a message to the channel at a specified queue with a specific
        message.

        :param queue_name: the name of the queue where the message will be
        sent.
        :param message: the message to be sent and stored in the queue.
        :return: Nothing
        """

        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def close_connection(self):
        self.connection.close()
