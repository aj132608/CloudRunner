import pika

from tests.queue_tests.sample_task import SampleTask


class QueueServer:
    def __init__(self, queue_name, endpoint="localhost"):
        self.connection = None
        self.channel = None
        self.queue_name = queue_name
        self.endpoint = endpoint
        self.task_obj = SampleTask()

    def establish_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.endpoint))

        self.channel = self.connection.channel()

    def create_queue(self):
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        print(f" [x] Recieved {body}")

        # Some task is going to start.
        number = self.task_obj.fibonacci(10)

        print(f"fib(10) = {number}")

        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def create_sample_response(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback)

    def start_server(self):
        self.establish_connection()
        self.create_queue()
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.create_sample_response()
        self.channel.start_consuming()
