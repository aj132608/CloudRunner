from services.queuingservices.rabbitmq.queue_server import QueueServer

if __name__ == "__main__":
    queue_obj = QueueServer("test_queue", exchange_name="logs", exchange_type="fanout")

    try:
        queue_obj.start_server()
        print("Test Passed")
    except:
        print("Test Failed")
