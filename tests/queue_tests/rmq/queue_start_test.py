from queue.rabbitmq.queue_server import QueueServer


if __name__ == "__main__":
    queue_obj = QueueServer(queue_name="ss_queue",
                            exchange_name="jobs",
                            exchange_type="direct",
                            endpoint="amqp://guest:guest@localhost")

    try:
        queue_obj.start_server()
        print("Test Passed")
    except Exception as e:
        print("Test Failed")
        print(f"Exception: {e}")
