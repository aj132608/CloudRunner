from services.queuingservices.rabbitmq.task_submit import TaskSubmit


def submit_n_tasks(obj, n):
    for task_num in range(1, n+1):
        obj.submit(message=f"{task_num}")


if __name__ == "__main__":
    # args = "ss_queue", "jobs", "direct", "amqp://guest:guest@localhost"
    task_obj = TaskSubmit(queue_name="ss_queue",
                          exchange="jobs",
                          endpoint="amqp://guest:guest@localhost")

    try:
        submit_n_tasks(task_obj, 10)
        print("Test Passed")
    except:
        print("Test Failed")
