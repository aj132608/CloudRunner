import pika
import uuid


class TaskSubmit:
    def __init__(self, queue_name, message, endpoint="localhost"):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.queue_name = queue_name
        self.endpoint = endpoint
        self.message = message
        self.response = "0"
        self.corr_id = ""

    def establish_connection(self):
        """

        Establishes a connection with the queue at the given or default
        endpoint and creates a channel there.

        :param endpoint:
        :return: Nothing
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.endpoint))

        self.channel = self.connection.channel()

    def declare_queue(self):
        """

        Declares the callback queue and starts a consume.

        :param: queue_name
        :return: Nothing
        """
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self):
        """

        :return:
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=self.message)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def submit(self):
        self.establish_connection()
        self.declare_queue()
        self.call()
        print(f"Response: {self.response}")
