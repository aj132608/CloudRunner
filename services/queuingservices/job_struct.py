
class JobStruct:
    """
    This class describes the path for the Job
    structure.
    """
    def __init__(self, storage_config, bucket_name, experient_id):
        """

        :param storage_config: The storage config should be of the format ->
        {
            "type": "s3",
            "endpoint": "xxx.com:port",
            "env": {

            }
        }
        :param bucket_name:
        :param experient_id:
        """
        self.storage_config = storage_config
        self.bucket_name = bucket_name
        self.experiment_id = experient_id
