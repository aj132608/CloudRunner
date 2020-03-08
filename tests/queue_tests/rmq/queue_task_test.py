from queuingservices.rabbitmq.publisher import Publisher


def submit_n_tasks(obj, n):
    for task_num in range(1, n+1):
        response = obj.send_message(message=f"{task_num}",
                                    queue_name="rabbit_queue_1",
                                    exchange_name="rabbit_exchange_1")


if __name__ == "__main__":
    task_obj = Publisher(endpoint="amqp://guest:guest@0.tcp.ngrok.io:12474")

    try:
        submit_n_tasks(task_obj, 10)
        print("Test Passed")
    except Exception as e:
        print("Test Failed")
        print(f"Exception: {e}")
