import pika


class PracticeWorker:
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

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=endpoint))
        self.channel = self.connection.channel()

    def create_sample_queue(self, queue_name):
        """

        Declares a queue on the previously established channel and names it
        whatever is passed in.

        :param queue_name: user specified name for the queue
        :return: Nothing
        """
        self.channel.queue_declare(queue=queue_name, durable=True)

    @staticmethod
    def queue_callback(ch, method, properties, body):
        print(f"body: {body}")
        print("Done!")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def create_sample_response(self, queue_name):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=PracticeWorker.queue_callback)

    def start_consuming(self):
        self.channel.start_consuming()