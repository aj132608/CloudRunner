from servicecommon.environment_utils import extract_environment_variables
from storage.aws.s3_store import S3Storage
from storage.azure.azure_store import AzureStorage
from storage.gcloud.gcloud_store import GCloudStorage

SUPPORTED_STORAGES = ("minio", "s3", "gcloud", "azure", "local")


class StorageCreator:

    def __init__(self, storage_config):
        """
        The constructor validates and extracts the environment variables.
        """
        self.storage_config = storage_config
        if "type" not in self.storage_config.keys():
            raise ValueError("Storage type not found. "
                             "Will attempt to use Local storage")

        self.storage_type = storage_config.get("type", "local")

        assert self.storage_type in SUPPORTED_STORAGES, \
            "Storage type not supported"

    def build_storage_object(self):
        """
        This function builds in the Storage object according to
        the type of storage specified.
        :returns storage_obj: Storage object of the appropriate Cloud
        provider
        """
        credentials = self.storage_config['env']
        if self.storage_type in ("minio", "s3"):
            credentials["endpoint_url"] = \
                self.storage_config["endpoint_url"]
            credentials["region"] = \
                self.storage_config["region"]
            storage_obj = S3Storage(credentials)
        elif self.storage_type == "gcloud":
            storage_obj = GCloudStorage(credentials)
        elif self.storage_type == "azure":
            storage_obj = AzureStorage(credentials)
        else:
            # Implement Local Storage here
            storage_obj = None

        return storage_obj



