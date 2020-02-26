import pika


class QueueServer:

    def __init__(self, queue_name, exchange_name, exchange_type,
                 endpoint="localhost"):

        self.connection = None
        self.channel = None
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.endpoint = endpoint
        self.worker_busy = False

    def _establish_connection(self, endpoint=None):
        if endpoint is None:
            endpoint = self.endpoint

        params = pika.URLParameters(endpoint)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

    def _declare_queue(self, queue_name=None):
        if queue_name is None:
            queue_name = self.queue_name

        # Establish the queue
        self.channel.queue_declare(queue=queue_name, durable=True)

    def _declare_exchange(self, exchange_name=None, queue_name=None):
        if exchange_name is None:
            exchange_name = self.exchange_name

        if queue_name is None:
            queue_name = self.queue_name

        # Establish the exchange
        self.channel.exchange_declare(exchange=exchange_name,
                                      exchange_type=self.exchange_type)

        # Bind the exchange to the queue
        self.channel.queue_bind(exchange=exchange_name,
                                queue=queue_name)

    def callback(self, ch, method, props, body):
        print(f" [x] Recieved {body}")

        self.worker_busy = True

        # stop consuming
        # self._stop_consuming()

        QueueServer.run_task()

        # self._start_consuming()

        print(" [x] Done")
        self.worker_busy = False
        # self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def _start_consuming(self, queue_name=None):
        if queue_name is None:
            queue_name = self.queue_name

        # print("Made it to start_consuming.")
        # print(f"queue name: {queue_name}")

        try:
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.callback,
                auto_ack=True,
                consumer_tag="current consumer")
            # # import pdb; pdb.set_trace()
            self.channel.start_consuming()

        except KeyboardInterrupt:
            print("Exiting gracefully")
            self.connection.close()

    def _stop_consuming(self, queue_name=None):
        if queue_name is None:
            queue_name = self.queue_name

        # print("Stopping Consumption")
        self.channel.basic_cancel(
            queue=queue_name, callback=self._worker_busy_callback)

    def _worker_busy_callback(self):
        self.worker_busy = True
        # print("Worker is currently busy.")

    def start_server(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self._establish_connection()
        self._declare_queue()
        self._declare_exchange()
        self._start_consuming()

    @staticmethod
    def run_task():
        """
        blank slate function to execute something

        :return:
        """
        import time
        from tests.queue_tests.sample_task import SampleTask

        task_obj = SampleTask()

        try:
            number = task_obj.fibonacci(10)

            print(f"fib(10) = {number}")
        except:
            print("There was an error in executing the task.")


# qs = QueueServer("ss_queue", "jobs", "direct", "amqp://guest:guest@localhost")
# qs.start_server()
# qs.start_consuming()

