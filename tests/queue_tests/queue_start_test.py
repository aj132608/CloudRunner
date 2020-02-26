from services.queuingservices.rabbitmq.queue_server import QueueServer


if __name__ == "__main__":
    # args = "ss_queue", "jobs", "direct", "amqp://guest:guest@localhost"
    # import pdb; pdb.set_trace()
    queue_obj = QueueServer(queue_name="ss_queue",
                            exchange_name="jobs",
                            exchange_type="direct",
                            endpoint="amqp://guest:guest@localhost")

    try:
        queue_obj.start_server()
        print("Test Passed")
    except Exception as e:
        print("Test Failed ", e)
