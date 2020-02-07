import pika


class Recieve:
    def __init__(self):
        self.connection = None
        self.channel = None

    def establish_connection(self):
        """
        establishes the inital connection with the Rabbitmq server
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def create_sample_queue(self):
        self.channel.queue_declare(queue='hello')

    def callback(self, ch, method, properties, body):
        print(f" [x] Recieved {body}")

    def recieve_sample_message(self):
        self.channel.basic_consume(queue='hello',
                                   on_message_callback=self.callback,
                                   auto_ack=True)

    def recieve_routine(self):
        self.establish_connection()
        self.create_sample_queue()
        self.recieve_sample_message()
        self.channel.start_consuming()


if __name__ == "__main__":
    recieve_obj = Recieve()
    recieve_obj.recieve_routine()
