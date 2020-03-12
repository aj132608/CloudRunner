class JobStorageInterface:
    """
    Takes in the user's storage configuration and gets the appropriate
    storage object from either the submitted jobs or the completed jobs.
    """

    def __init__(self, storage_obj):
        self._storage_obj = storage_obj
    
    def put_job_data(self, bucket, username, project_id, experiment_id, job_id, local_path, variant):
        """
        This function pushes the job data.
        :param bucket:
        :param username:
        :param project_id:
        :param experiment_id:
        :param job_id:
        :param local_path:
        :param variant: submission or completion
        :return:
        """
        # Construct the key to send to the storage interface class
        key = f"{username}/{project_id}/{experiment_id}/{variant}/{job_id}.tar"
        self._storage_obj.persist_file(key=key,
                                       bucket=bucket,
                                       local_file_path=local_path)

    def get_job_data(self, bucket, username, project_id, experiment_id, job_id, local_path, variant):
        """

        This function downloads job data based on the following arguments

        :param bucket:
        :param username:
        :param project_id:
        :param experiment_id:
        :param job_id:
        :param local_path:
        :param variant: submission or completion
        :return:
        """
        # Construct the key to send to the storage interface class
        key = f"{username}/{project_id}/{experiment_id}/{variant}/{job_id}.tar"
        self._storage_obj.download_file(key=key,
                                        bucket=bucket,
                                        local_file_path=local_path)
