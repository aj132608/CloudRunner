from queuingservices.managers.queue_master import QueueMaster
from servicecommon.persistor.local.json.json_persistor import JsonPersistor
from storage.storage_creator import StorageCreator

import sys

if __name__ == '__main__':
    """
    This server is responsible to initialize the 
    worker.
    """

    original_stdout = sys.stdout
    log_file = open("/.mineai/subscriber_logs.txt", "w")
    sys.stdout = log_file

    # Load Configs
    config_path = "/.mineai/configs"
    queue_config_restorer = JsonPersistor(None,
                                          base_file_name='queue_config', folder=config_path)
    queue_config = queue_config_restorer.restore()

    storage_config_restorer = JsonPersistor(None,
                                          base_file_name='storage_config', folder=config_path)
    storage_config = storage_config_restorer.restore()

    storage_object = StorageCreator(storage_config).build_storage_object()

    # Start Queue Subscriber
    queue_master = QueueMaster(queue_config=queue_config,
                               storage_obj=storage_object)
    queue_subscriber = queue_master.build_subscribe_object()

    print("Starting Queue Server")
    queue_subscriber.start_server()

    sys.stdout = original_stdout
    log_file.close()