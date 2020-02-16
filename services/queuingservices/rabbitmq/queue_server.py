import pika

from tests.queue_tests.sample_task import SampleTask


class QueueServer:
    def __init__(self, queue_name, exchange_name, exchange_type,
                 endpoint="localhost"):
        self.connection = None
        self.channel = None
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.endpoint = endpoint
        self.task_obj = SampleTask()

    def establish_connection(self):
        params = pika.URLParameters(self.endpoint)
        self.connection = pika.BlockingConnection(params)

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name, durable=True)

        self.channel.exchange_declare(exchange=self.exchange_name,
                                      exchange_type=self.exchange_type)

        self.channel.queue_bind(exchange=self.exchange_name,
                                queue=self.queue_name)

    def callback(self, channel, method, properties, body):
        print(f" [x] Recieved {body}")

        # Some task is going to start.
        number = self.task_obj.fibonacci(10)

        print(f"fib(10) = {number}")

        print(" [x] Done")
        # channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback)

    def start_server(self):
        self.establish_connection()
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)

        self.channel.start_consuming()

qs = QueueServer("ss_queue", "jobs", "direct", "amqp://guest:guest@0.tcp.ngrok.io:15831")
qs.start_server()
qs.consume()

