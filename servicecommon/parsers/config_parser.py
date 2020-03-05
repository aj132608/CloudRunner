import os

from servicecommon.persistor.local.json.json_persistor import JsonPersistor


class ConfigParser:

    def __init__(self, config_path):
        """

        :param config_path:
        """
        self.config_path = config_path

        config_path = os.path.dirname(self.config_path)

        config_name = os.path.basename(self.config_path)
        config_name = os.path.splitext(config_name)[0]
        json_restorer = JsonPersistor(None, base_file_name=config_name,
                                      folder=config_path)
        self.config = json_restorer.restore()

        self.compute_config = None
        self.computing_environments = self.get_computing_environments()

    def get_computing_environments(self):
        """

        :return:
        """
        self.compute_config = self.config.get("compute")
        compute_types = self.compute_config.keys()

        for compute_type in compute_types:
            assert compute_type in ("GCloud", "AWS", "local")

        return list(compute_types)

    def get_compute_config(self, compute_type):
        """

        :return:
        """
        return self.compute_config.get(compute_type)

    def get_compute_resource_allocation(self, compute_type):
        """

        :return:
        """
        compute_config = self.get_compute_config(compute_type)
        resources = compute_config.get("resources")

        return resources

    def get_compute_env(self, compute_type):
        """

        :return:
        """
        compute_config = self.get_compute_config(compute_type)
        env = compute_config.get("env")

        return env

    def get_storage_config(self):
        """

        :return:
        """
        return self.config.get("storage")

    def get_queue_config(self):
        """

        :return:
        """
        return self.config.get("queuingservices")

    def get_storage_type(self):
        return self.get_storage().get("type")
