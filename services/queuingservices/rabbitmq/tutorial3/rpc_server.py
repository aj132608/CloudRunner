import pika


class RPCServer:
    def __init__(self):
        self.connection = None
        self.channel = None

    def establish_connection(self, endpoint):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=endpoint))

        self.channel = self.connection.channel()

    def create_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name)

    @staticmethod
    def fib(n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return RPCServer.fib(n - 1) + RPCServer.fib(n - 2)

    @staticmethod
    def on_request(ch, method, props, body):
        n = int(body)

        print(" [.] fib(%s)" % n)
        response = RPCServer.fib(n)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=
                                                         props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def message_handler(self, queue_name):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue_name,
                                   on_message_callback=RPCServer.on_request)

        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()


if __name__ == "__main__":
    rpc_obj = RPCServer()
    rpc_obj.establish_connection('localhost')
    rpc_obj.create_queue('rpc_queue')
    rpc_obj.message_handler('rpc_queue')
