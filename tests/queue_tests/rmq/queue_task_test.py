from queuingservices.rabbitmq.publisher import Publisher
from queuingservices.message_struct import MessageStruct


if __name__ == "__main__":
    message_struct = MessageStruct(bucket_name="cloudrunneralex",
                                   username="alex.jirovsky",
                                   experiment_id="experiment0",
                                   project_id="project0",
                                   job_id="job0",
                                   completion=True,
                                   submission=False)

    task_obj = Publisher(endpoint="amqp://guest:guest@0.tcp.ngrok.io:12474")

    try:
        task_obj.send_message(message=message_struct.__dict__,
                              queue_name="rabbit_queue_1",
                              exchange_name="rabbit_exchange_1")
        print("Test Passed")
    except Exception as e:
        print("Test Failed")
        print(f"Exception: {e}")

