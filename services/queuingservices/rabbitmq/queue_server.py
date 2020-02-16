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
        self.channel.queue_declare(queue=self.queue_name)

    def on_request(self, ch, method, props, body):

        print(" [.] task_id(%s)" % body)

        # for index in range(1, 5):
        #     self.task_obj.fibonacci(index)
        self.task_obj.fibonacci(5)

        response = f"{self.task_obj.get_sequence()}"

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=
                                                         props.correlation_id),
                         body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def message_handler(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name,
                                   on_message_callback=self.on_request)

        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()

    def start_server(self):
        self.establish_connection()
        self.create_queue()
        self.message_handler()
