from services.queuingservices.rabbitmq.task_submit import TaskSubmit

if __name__ == "__main__":
    task_obj = TaskSubmit("test_queue", "task_12345")

    try:
        task_obj.submit()
        print("Test Passed")
    except:
        print("Test Failed")
