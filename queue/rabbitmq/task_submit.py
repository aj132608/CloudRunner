import pika


class TaskSubmit:
    def __init__(self, queue_name, exchange="job", endpoint="localhost"):
        self.connection = None
        self.channel = None
        self.exchange = exchange
        self.queue_name = queue_name
        self.endpoint = endpoint

    def establish_connection(self):
        """

        Establishes a connection with the queue at the given or default
        endpoint and creates a channel there.

        :return: Nothing
        """
        params = pika.URLParameters(self.endpoint)
        self.connection = pika.BlockingConnection(params)

        self.channel = self.connection.channel()

    def create_queue(self):
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def publish_message(self, message):
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        print(f" [x] Sent {message}")

    def submit(self, message):
        self.establish_connection()
        self.create_queue()
        self.publish_message(str(message))
        self.connection.close()

# ts = TaskSubmit("new_q", "job", "amqp://guest:guest@0.tcp.ngrok.io:18109")
# ts.submit()
