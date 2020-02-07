import pika


class Send:
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

    def send_sample_message(self):
        self.channel.basic_publish(exchange='',
                                   routing_key='hello',
                                   body='Hello World!')

    def send_routine(self):
        self.establish_connection()
        self.create_sample_queue()
        self.send_sample_message()
        self.connection.close()


if __name__ == "__main__":
    send_obj = Send()
    send_obj.send_routine()
