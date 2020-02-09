import pika


class PracticeQueue:
    def __init__(self):
        self.connection = None
        self.channel = None

    def establish_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def tutorial_test_1(self):
        self.establish_connection()


if __name__ == "__main__":
    queue_obj = PracticeQueue()
    queue_obj.tutorial_test_1()
