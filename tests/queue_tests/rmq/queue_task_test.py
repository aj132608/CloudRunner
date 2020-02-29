from queuingservices.rabbitmq.publisher import Publisher


def submit_n_tasks(obj, n):
    for task_num in range(1, n+1):
        response = obj.send_message(message=f"{task_num}",
                                    queue_name="project_queue",
                                    exchange_name="project_exchange")


if __name__ == "__main__":
    task_obj = Publisher(endpoint="amqp://guest:guest@localhost")

    try:
        submit_n_tasks(task_obj, 10)
        print("Test Passed")
    except Exception as e:
        print("Test Failed")
        print(f"Exception: {e}")
