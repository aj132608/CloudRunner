import os

from servicecommon.environment_utils import extract_environment_variables
from servicecommon.persistor.local.json.json_persistor import JsonPersistor


class ConfigHandler:
    """
    This class handles the Config required by Cloud DSM
    to extract the respective things needed.
    """

    def __init__(self, config_path, project_name):
        """
        The constructor initializes the config from
        the config path.
        :param config_path:
        """
        config_path = config_path
        config_folder = os.path.dirname(config_path)
        config_name = os.path.basename(config_path)
        config_name = os.path.splitext(config_name)[0]
        json_restorer = JsonPersistor(None, base_file_name=config_name,
                                      folder=config_folder)
        self.config = json_restorer.restore()
        self.project_name = project_name

        self.config = self.extract_env()
        self.initialize_queue_default()

    def get_compute_config(self):
        """
        This function returns the compute config
        """
        return self.config.get("compute")

    def get_compute_type_config(self, compute_type):
        """
        This function returns the config of a compute
        type.
        """
        compute_config = self.get_compute_config()
        return compute_config.get(compute_type)

    def extract_env(self):
        """
        This function extracts the required environment variables and
        replaces them in the config.
        :returns restored_env_config: Config with the restored env vars
        """
        import copy
        restored_env_config = {}

        config_copy = copy.deepcopy(self.config)

        # Restore Compute
        compute_config = config_copy.get("compute")
        for compute in compute_config:
            config = compute_config[compute]
            env = config.get("env", None)
            if env is not None:
                config["env"] = extract_environment_variables(env)
            restored_env_config["compute"] = compute_config

        # Restore Storage
        storage_config = config_copy.get("storage_config")
        storage_env = storage_config.get("env", None)
        if storage_env is not None:
            storage_config["env"] = extract_environment_variables(storage_env)
        restored_env_config["storage"] = storage_config

        # Restore Queue
        queue_config = config_copy.get("queue_config")
        queue_env = queue_config.get("env", None)
        if queue_env is not None:
            queue_config["env"] = extract_environment_variables(queue_env)
        restored_env_config["queue"] = queue_config

        return restored_env_config

    def initialize_queue_default(self):
        """
        This function is responsible for initializing the
        missing values in queue and set the defaults/
        :returns nothing:
        """
        queue_config = self.get_queue_config()
        queue_type = queue_config.get("type")

        if queue_type == "rmq":
            queue_name = queue_config.get("queue_name", None)
            exchange_name = queue_config.get("exchange_name", None)

            if queue_name is None:
                queue_config["queue_name"] = f"mine_ai_{self.project_name}"

            if exchange_name is None:
                queue_config["exchange_name"] = f"mine_ai_{self.project_name}"

        elif queue_type == "sqs":
            queue_name = queue_config.get("queue_name", None)
            queue_url = queue_config.get("queue_url", None)

            if not queue_name and \
                    not queue_url:
                queue_config["queue_name"] = f"mine_ai_{self.project_name}_queue"

        else:
            pass

    def get_storage_config(self):
        """
        This function returns the storage config
        """
        return self.config.get("storage")

    def get_queue_config(self):
        """
        This function returns the queue config
        """
        return self.config.get("queue")

    def get_master_node_config(self):
        """
        This function returns the master node config if
        availaible.
        """
        return self.config.get("master_node", None)
