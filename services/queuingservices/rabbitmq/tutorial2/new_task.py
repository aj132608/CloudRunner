import pika
import sys


class NewTask:
    def __init__(self, endpoint=None, queue_name=None, message=None):
        self.connection = None
        self.channel = None
        self.endpoint = endpoint
        self.queue_name = queue_name
        self.message = message

        if self.endpoint is None:
            self.endpoint = 'localhost'

        if self.queue_name is None:
            self.queue_name = 'task_queue'

        if self.message is None:
            self.message = "task-12345"

    def establish_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.endpoint))
        self.channel = self.connection.channel()

    def create_sample_queue(self):
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def create_sample_message(self):
        message = ' '.join(sys.argv[1:]) or self.message

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
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
