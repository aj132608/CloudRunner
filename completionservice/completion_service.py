from queuingservices.managers.queue_master import QueueMaster
from completionservice.completion_storage_interface import CompletionStorageInterface


class CompletionService:
    def __init__(self, queue_config, storage_config):
        self.queue_config = queue_config
        self.storage_config = storage_config
        self._subscriber = self._get_subscriber()
        self._subscriber.start_server()

    def _get_subscriber(self):
        """

        Retrieves the subscribe object specified by the user

        :return:
        """
        queue_obj = QueueMaster(queue_config=self.queue_config)

        return queue_obj.build_subscribe_object()

    def retrieve_job_data(self, bucket, username, project_id,
                          experiment_id, job_id, local_path):
        """

        This function will download a job file to a specified location with
        a specified file name locally.

        :param bucket:
        :param username:
        :param project_id:
        :param experiment_id:
        :param job_id:
        :param local_path:
        :return:
        """
        storage_master_obj = CompletionStorageInterface(storage_config=
                                                        self.storage_config)

        storage_master_obj.get_job_data(bucket=bucket,
                                        username=username,
                                        project_id=project_id,
                                        experiment_id=experiment_id,
                                        job_id=job_id,
                                        local_path=local_path)
