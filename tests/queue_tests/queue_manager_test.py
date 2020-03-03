from queuingservices.queue_manager import QueueManager
from servicecommon.persistor.local.json.json_persistor import JsonPersistor

if __name__ == "__main__":
    try:
        # Get the queue config dictionaries
        rmq_restore = JsonPersistor(dict=None, base_file_name="rmq_queue_config", folder="creds/")
        sqs_restore = JsonPersistor(dict=None, base_file_name="sqs_queue_config", folder="creds/")
        rmq_queue_config = rmq_restore.restore()
        sqs_queue_config = sqs_restore.restore()

        # get the QueueOrchestrator objects by sending them the corresponding
        # queue config dictionaries
        rmq_orchestrator_obj = QueueManager(queue_config=rmq_queue_config)
        sqs_orchestrator_obj = QueueManager(queue_config=sqs_queue_config)

        # get the correct Subscriber objects
        rmq_queue_obj = rmq_orchestrator_obj.build_queue_object()
        sqs_queue_obj = sqs_orchestrator_obj.build_queue_object()

        print(f"rmq subscriber object: {rmq_queue_obj}")
        print(f"sqs subscriber object: {sqs_queue_obj}")
    except Exception as e:
        print("Test Failed.")
        print(f"Exception: {e}")
