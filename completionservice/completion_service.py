from queuingservices.managers.queue_master import QueueMaster
from servicecommon.persistor.local.json.json_persistor import JsonPersistor
from storage.storage_creator import StorageCreator


class CompletionService:
    """
    This class spins up a subscriber that is responsible
    for restoring the results of the jobs submitted on the
    local file system.
    """
    def __init__(self, queue_config, storage_config):
        """
        The constructor initializes this server and
        starts listening for messages describing complete
        jobs.
        :param queue_config:
        :param storage_config:
        """
        self.queue_config = queue_config
        self.storage_config = storage_config

        self.storage_obj = StorageCreator(self.storage_config).build_storage_object()

        self._subscriber = self._get_subscriber()
        self._subscriber.start_server()

    def _get_subscriber(self):
        """
        Retrieves the subscribe object specified by the user
        :returns subscriber_object: The subscriber object
        """
        queue_obj = QueueMaster(queue_config=self.queue_config,
                                storage_obj=self.storage_obj)
        subscriber_object = queue_obj.build_subscribe_object()
        return subscriber_object


if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser(description='This server is the completion Server')
    parser.add_argument('--queue_config_path',
                        help='Path of JSON Describing the Queue config')
    parser.add_argument('--storage_config_path',
                        help='Path of JSON Describing the Storage config')
    parser.add_argument('--project_name',
                        help='Name of the Project.')
    args = parser.parse_args()

    project_name = args.project_name

    queue_config_path = args.queue_config_path
    queue_config_name = os.path.basename(queue_config_path)
    queue_config_name_without_ext = os.path.splitext(queue_config_name)[0]
    queue_config_folder = os.path.dirname(queue_config_path)

    storage_config_path = args.storage_config_path
    storage_config_name = os.path.basename(storage_config_path)
    storage_config_name_without_ext = os.path.splitext(storage_config_name)[0]
    storage_config_folder = os.path.dirname(storage_config_path)

    json_restorer = JsonPersistor(None, base_file_name=queue_config_name_without_ext, folder=queue_config_folder)
    queue_config = json_restorer.restore()

    json_restorer = JsonPersistor(None, base_file_name=storage_config_name_without_ext, folder=storage_config_folder)
    storage_config = json_restorer.restore()

    CompletionService(queue_config, storage_config)




