from queuingservices.managers.queue_master import QueueMaster
from servicecommon.persistor.local.json.json_persistor import JsonPersistor

if __name__ == "__main__":
    try:
        # Get the queue config dictionaries
        rmq_restore = JsonPersistor(dict=None,
                                    base_file_name="rmq_queue_config",
                                    folder="creds/")
        sqs_restore = JsonPersistor(dict=None,
                                    base_file_name="sqs_queue_config",
                                    folder="creds/")

        rmq_queue_config = rmq_restore.restore()
        sqs_queue_config = sqs_restore.restore()

        rmq_queue_obj = QueueMaster(queue_config=rmq_queue_config)
        sqs_queue_obj = QueueMaster(queue_config=sqs_queue_config)

        rmq_sub = rmq_queue_obj.build_subscribe_object()
        rmq_pub = rmq_queue_obj.build_publisher_object()
        rmq_life = rmq_queue_obj.build_lifecycle_object()

        sqs_sub = sqs_queue_obj.build_subscribe_object()
        sqs_pub = sqs_queue_obj.build_publisher_object()
        sqs_life = sqs_queue_obj.build_lifecycle_object()

        print(f"RabbitMQ Subscriber: {rmq_sub}")
        print(f"RabbitMQ Publisher: {rmq_pub}")
        print(f"RabbitMQ Lifecycle: {rmq_life}")
        print(f"SQS Subscriber: {sqs_sub}")
        print(f"SQS Publisher: {sqs_pub}")
        print(f"SQS Lifecycle: {sqs_life}")

    except Exception as e:
        print("Test Failed.")
        print(f"Exception: {e}")