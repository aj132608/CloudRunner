SUPPORTED_QUEUES = ("sqs", "rmq", "local")


class QueueLifecycleManager:
    """

    This class will be sent a queue config dictionary and determine which
    queue to use by the information contained in that config.

    Acceptable queue types:
    - sqs (AWS Simple Queuing Service)
    - rmq (Rabbit MQ Queuing Service)
    - local (locally run queuing service)

    """

    def __init__(self, queue_config, storage_obj=None):
        """

        The constructor will take in the queue and storage config files and
        validate them.

        :param queue_config:
        :param storage_obj:
        """
        self.queue_config = queue_config
        self.storage_obj = storage_obj

        if "type" not in self.queue_config.keys():
            raise ValueError(f"Queue type not found. Please update creds.json"
                             f" with one of the following supported queue "
                             f"types.\n{SUPPORTED_QUEUES}")

        self.queue_type = queue_config['type']

        assert self.queue_type in SUPPORTED_QUEUES, \
            f"Queue Type {self.queue_type} not supported"

    def build_lifecycle_object(self):
        """

        This function builds the queue object according to the type of queue
        specified in the config file.

        :return: queue_obj: Queue object of the desired type

        """
        if self.queue_type == "sqs":
            # Retrieve the SQS lifecycle object
            from queuingservices.sqs.queue_lifecycle import QueueLifecycle

            credentials_dict = self._get_sqs_credentials_dict()
            queue_obj = QueueLifecycle(credentials_dict=credentials_dict)
        elif self.queue_type == "rmq":
            # Retrieve the RMQ lifecycle object
            from queuingservices.rabbitmq.queue_lifecycle import QueueLifecycle

            endpoint = self.queue_config['endpoint']
            queue_obj = QueueLifecycle(endpoint=endpoint)
        else:
            queue_obj = None

        return queue_obj

    def _get_sqs_credentials_dict(self):
        """

        This function will construct a credentials dictionary that corresponds
        to the format outlined in the SQS Documentation.

        Example:
        {
            "access_key": "YOUR_ACCESS_KEY",
            "secret_key": "YOUR_SECRET_KEY",
            "region": "us-west-2",
            "user_id": "YOUR_USER_ID",
            "queue_name": "cdsm_queue_1",
            "queue_url": "https://region.queue.amazonaws.com/user_id/queue_name"
        }

        :return: formatted credentials dictionary like the one shown above
        """

        credentials_dict = {}

        env_dict = self.queue_config['env']

        credentials_dict['access_key'] = env_dict\
            .get('cdsm_queue_access_key')

        credentials_dict['secret_key'] = env_dict\
            .get('cdsm_queue_secret_key')

        credentials_dict['region'] = self.queue_config\
            .get('region')

        if "queue_name" in self.queue_config.keys():
            credentials_dict['queue_name'] = self.queue_config\
                .get('queue_name')

        if "queue_url" in self.queue_config.keys():
            credentials_dict['queue_url'] = self.queue_config\
                .get('queue_url')

        if "user_id" in self.queue_config.keys():
            credentials_dict['user_id'] = self.queue_config\
                .get('user_id')

        return credentials_dict
