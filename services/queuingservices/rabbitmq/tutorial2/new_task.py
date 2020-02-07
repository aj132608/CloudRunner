import pika
import sys


class NewTask:
    def __init__(self):
        self.connection = None
        self.channel = None

    def establish_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

    def create_sample_queue(self):
        self.channel.queue_declare(queue='task_queue', durable=True)

    def create_sample_message(self):
        message = ' '.join(sys.argv[1:]) or "Hello World!"

        self.channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        print(f" [x] Sent {message}")

    def new_task_routine(self):
        self.establish_connection()
        self.create_sample_queue()
        self.create_sample_message()
        self.connection.close()


if __name__ == "__main__":
    task_obj = NewTask()
    task_obj.new_task_routine()
