from queuingservices.rabbitmq.subscriber import Subscriber
from queuingservices.rabbitmq.queue_lifecycle import QueueLifecycle
# 0.tcp.ngrok.io:10503

if __name__ == "__main__":
    endpoint = "amqp://guest:guest@localhost"
    queue_name = "project_queue"
    exchange_name = "project_exchange"

    queue_obj = QueueLifecycle(endpoint=endpoint)

    response = queue_obj.create_queue(queue_name=queue_name)

    if response:
        print("Queue was successfully created!")

    response = queue_obj.create_and_bind_exchange(queue_name=queue_name,
                                                  exchange_name=exchange_name)

    if response:
        print("Exchange was successfully created and bound!")

    queue_obj = Subscriber(queue_name=queue_name,
                           endpoint=endpoint)

    try:
        queue_obj.start_server()
        print("Test Passed")
    except Exception as e:
        print("Test Failed")
        print(f"Exception: {e}")
