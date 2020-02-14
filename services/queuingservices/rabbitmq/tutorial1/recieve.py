import pika


class Receive:
    def __init__(self):
        self.connection = None
        self.channel = None

    def establish_connection(self):
        """
        establishes the initial connection with the Rabbitmq server
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def create_sample_queue(self):
        self.channel.queue_declare(queue='hello')

    def callback(self, ch, method, properties, body):
        print(f" [x] Received {body}")

    def receive_sample_message(self):
        self.channel.basic_consume(queue='hello',
                                   on_message_callback=self.callback,
                                   auto_ack=True)

    def receive_routine(self):
        self.establish_connection()
        self.create_sample_queue()
        self.receive_sample_message()
        self.channel.start_consuming()


if __name__ == "__main__":
    receive_obj = Receive()
    receive_obj.receive_routine()
