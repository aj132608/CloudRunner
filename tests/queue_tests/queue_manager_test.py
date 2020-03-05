from queuingservices.managers.queue_subscriber_manager import QueueSubscriberManager
from queuingservices.managers.queue_publisher_manager import QueuePublisherManager
from queuingservices.managers.queue_lifecycle_manager import QueueLifecycleManager
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

        # get the QueueOrchestrator objects by sending them the corresponding
        # queue config dictionaries
        rmq_sub_manage = QueueSubscriberManager(queue_config=rmq_queue_config)
        rmq_pub_manage = QueuePublisherManager(queue_config=rmq_queue_config)
        rmq_life_manage = QueueLifecycleManager(queue_config=rmq_queue_config)
        sqs_sub_manage = QueueSubscriberManager(queue_config=sqs_queue_config)
        sqs_pub_manage = QueuePublisherManager(queue_config=sqs_queue_config)
        sqs_life_manage = QueueLifecycleManager(queue_config=sqs_queue_config)

        # get the correct queue objects
        rmq_subscriber = rmq_sub_manage.build_queue_object()
        rmq_publisher = rmq_pub_manage.build_queue_object()
        rmq_lifecycle = rmq_life_manage.build_queue_object()
        sqs_subscriber = sqs_sub_manage.build_queue_object()
        sqs_publisher = sqs_pub_manage.build_queue_object()
        sqs_lifecycle = sqs_life_manage.build_queue_object()

        # print out each object to confirm that the correct object was returned
        print(f"rmq subscriber object: {rmq_subscriber}")
        print(f"rmq publisher object: {rmq_publisher}")
        print(f"rmq lifecycle object: {rmq_lifecycle}")
        print(f"sqs subscriber object: {sqs_subscriber}")
        print(f"sqs publisher object: {sqs_publisher}")
        print(f"sqs lifecycle object: {sqs_lifecycle}")

    except Exception as e:
        print("Test Failed.")
        print(f"Exception: {e}")
