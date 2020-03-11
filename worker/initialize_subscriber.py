import sys
import os
sys.path.extend(os.getcwd())

from queuingservices.managers.queue_master import QueueMaster
from servicecommon.persistor.local.json.json_persistor import JsonPersistor
from storage.storage_creator import StorageCreator

if __name__ == '__main__':
    """
    This server is responsible to initialize the 
    worker.
    """

    import argparse
    import os

    parser = argparse.ArgumentParser(description='This server is the subscriber that receives'
                                                 'job messages from the submission Server')
    parser.add_argument('--queue_config_path',
                        help='Path of JSON Describing the Queue config that was used to '
                             'initialize the Submission Server Queue')
    parser.add_argument('--storage_config_path',
                        help='Path of JSON Describing the Storage config that was used to '
                             'initialize the Submission Server Storage')
    args = parser.parse_args()

    queue_config_path = args.queue_config_path

    queue_config_name = os.path.basename(queue_config_path)
    queue_config_name_without_ext = os.path.splitext(queue_config_name)[0]
    queue_config_folder = os.path.dirname(queue_config_path)

    storage_config_path = args.storage_config_path
    storage_config_name = os.path.basename(storage_config_path)
    storage_config_name_without_ext = os.path.splitext(storage_config_name)[0]
    storage_config_folder = os.path.dirname(storage_config_path)

    queue_config_restorer = JsonPersistor(None,
                                          base_file_name=queue_config_name_without_ext,
                                          folder=queue_config_folder)
    queue_config = queue_config_restorer.restore()

    print("Queue Config: ", queue_config)

    storage_config_restorer = JsonPersistor(None,
                                           base_file_name=storage_config_name_without_ext,
                                            folder=storage_config_folder)
    storage_config = storage_config_restorer.restore()

    print("Storage Config: ", storage_config)

    storage_object = StorageCreator(storage_config).build_storage_object()

    # Start Queue Subscriber
    queue_master = QueueMaster(queue_config=queue_config,
                               storage_obj=storage_object)
    queue_subscriber = queue_master.build_subscribe_object()

    print("Starting Queue Server")
    queue_subscriber.start_server()
