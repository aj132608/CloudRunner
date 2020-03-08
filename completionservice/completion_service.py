from queuingservices.managers.queue_master import QueueMaster
from storage.storage_creator import StorageCreator


class CompletionService:
    def __init__(self, queue_config, storage_config):
        self.queue_config = queue_config
        self.storage_config = storage_config

        self.storage_obj = StorageCreator(self.storage_config).build_storage_object()
        self._subscriber = self._get_subscriber()
        self._subscriber.start_server()

    def _get_subscriber(self):
        """

        Retrieves the subscribe object specified by the user

        :return:
        """
        queue_obj = QueueMaster(queue_config=self.queue_config,
                                storage_obj=self.storage_obj)

        return queue_obj.build_subscribe_object()


