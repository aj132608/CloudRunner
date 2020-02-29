from queue.rabbitmq.task_submit import TaskSubmit


def submit_n_tasks(obj, n):
    for task_num in range(1, n+1):
        obj.submit(message=f"{task_num}")


if __name__ == "__main__":
    task_obj = TaskSubmit(queue_name="ss_queue",
                          exchange="jobs",
                          endpoint="amqp://guest:guest@localhost")

    try:
        submit_n_tasks(task_obj, 10)
        print("Test Passed")
    except Exception as e:
        print("Test Failed")
        print(f"Exception: {e}")
