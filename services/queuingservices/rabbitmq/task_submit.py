import pika
import uuid


class TaskSubmit:
    def __init__(self, queue_name, message, endpoint="localhost"):
        self.connection = None
        self.channel = None
        self.queue_name = queue_name
        self.endpoint = endpoint
        self.message = message

    def establish_connection(self):
        """

        Establishes a connection with the queue at the given or default
        endpoint and creates a channel there.

        :return: Nothing
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.endpoint))

        self.channel = self.connection.channel()

    def create_queue(self):
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def publish_message(self):

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=self.message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        print(f" [x] Sent {self.message}")

    def submit(self):
        self.establish_connection()
        self.create_queue()
        self.publish_message()
        self.connection.close()
