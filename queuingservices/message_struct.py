class MessageStruct:
    """
    This class describes the path for the Message Struct that will be sent
    from the completion service.
    """

    def __init__(self, bucket_name, username, project_id, experiment_id, job_id, completion=True, submission=False):
        """
        :param bucket_name:
        :param username:
        :param project_id:
        :param experiment_id:
        :param job_id:
        """
        self.bucket_name = bucket_name
        self.username = username
        self.project_id = project_id
        self.experiment_id = experiment_id
        self.job_id = job_id
        self.completion = completion
        self.submission = submission
