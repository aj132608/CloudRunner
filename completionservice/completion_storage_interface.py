from storage.storage_creator import StorageCreator


class CompletionStorageInterface:
    def __init__(self, storage_config):
        """

        Takes in the user's storage configuration and gets the appropriate
        storage object.

        :param storage_config: User's configuration containing information
        on their desired storage.
        """
        self.storage_config = storage_config
        self._storage_obj = StorageCreator(storage_config=self.storage_config).build_storage_object()

    def get_job_data(self, bucket, username, project_id, experiment_id, job_id, local_path):
        """

        This function downloads job data based on the following arguments

        :param bucket:
        :param username:
        :param project_id:
        :param experiment_id:
        :param job_id:
        :param local_path:
        :return:
        """
        # Construct the key to send to the storage interface class
        key = f"/{username}/{project_id}/{experiment_id}/completion/{job_id}.tar"
        self._storage_obj.download_file(key=key,
                                        bucket=bucket,
                                        local_storage_path=local_path)
