import os

from fstracker.fs_tracker import FileSystemTracker
from servicecommon.parsers.config_parser import ConfigParser
from storage.aws.s3_store import S3Store
from storage.gcloud import GCloudStore
from services.queuingservices.rabbitmq.task_submit import TaskSubmit
from workermanager.aws_worker import, EC2WorkerManager
from workermanager.gcloud_worker import GCloudWorker


# GCLOUD CREDS: https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.171849056.175403659.1582490113-1979849865.1581803480

class InitializationService:

    def __init__(self, config_path, project_id,
                 persist_file_system=True,
                 create_instances=True, initialize_queue=True):
        """

        :param config_path:
        """
        self.config_path = config_path
        self.config_parser = ConfigParser(self.config_path)
        self.project_id = project_id

        self.computes = self.config_parser.get_computing_environments()
        self.storage_config = self.config_parser.get_storage_config()
        self.queue_config = self.config_parser.get_queue_config()

        self.storage_obj = self.set_storage_object()

        if persist_file_system:
            self.persist_inital_filesystem()

        if create_instances:
            self.create_instances()

        if initialize_queue:
            self.task_submitter = self.initialize_queue()

    def initialize_queue(self):
        """

        :return:
        """
        queue_config = self.config_parser.get_queue_config()
        if queue_config.get("type") == "rmq":
            task_submitter = TaskSubmit(queue_name=queue_config.get("queue_name"),
                                        exchange=queue_config.get("exchange_name"),
                                        endpoint=queue_config.get("endpoint_url"))
        task_submitter.establish_connection()
        return task_submitter

    def persist_inital_filesystem(self):
        """

        :return:
        """
        fs_tracker = FileSystemTracker(os.getcwd(),
                                       f"~/.cloudrunner/{self.project_id}/temp",
                                       self.storage_obj,
                                       project_name=self.project_id,
                                       project_id=self.project_id,
                                       config=self.config_parser.config,
                                       config_path=self.config_path)
        fs_tracker.persist()

    def create_instances(self):
        """

        :return:
        """
        if "AWS" in self.computes:
            aws_config = self.config_parser.get_compute_config("AWS")
            aws_worker = EC2WorkerManager(self.project_id, aws_config)
            aws_worker.create_workers(queue_name=None, )

        # if "GCloud" in self.computes:
        #     gcloud_creds = self._build_gcloud_creds()
        #     resource_dict = self.config_parser.get_compute_resource_allocation("GCloud")
        #     resource_dict["zone"] = self.config_parser.get_compute_config("GCloud").get("zone")
        #     gcloud_workers = GCloudWorker(gcloud_creds,
        #                                   resource_dict, self.project_id)
        #     gcloud_workers.create_workers()

    def _determine_storage(self):
        """

        :return:
        """
        storage_type = self.storage_config.get("type")
        if storage_type in ("s3", "minio"):
            return "AWS"
        elif storage_type in ["gcloud"]:
            return "GCloud"
        else:
            return "local"

    def _build_aws_storage_creds(self):
        """

        :return:
        """
        aws_env = self.storage_config.get("env")
        cdsm_aws_access_key = os.getenv(aws_env["cdsm_storage_access_key"])
        cdsm_aws_secret_key = os.getenv(aws_env["cdsm_storage_secret_key"])

        credentials_dict = {
            "access_key": cdsm_aws_access_key,
            "secret_key": cdsm_aws_secret_key,
            "endpoint_url": self.storage_config.get("endpoint_url"),
            "region": self.storage_config.get("region")
        }

        return credentials_dict

    def _build_aws_instance_creds(self):
        """

        :return:
        """
        aws_env = self.config_parser.get_compute_env("AWS")
        cdsm_aws_access_key = os.getenv(aws_env["cdsm_compute_access_key"])
        cdsm_aws_secret_key = os.getenv(aws_env["cdsm_compute_secret_key"])

        credentials_dict = {
            "access_key": cdsm_aws_access_key,
            "secret_key": cdsm_aws_secret_key
        }

        return credentials_dict

    def _build_gcloud_creds(self):
        """

        :return:
        """
        gcloud_env = self.config_parser.get_compute_env("GCloud")
        cdsm_google_cred_path = os.getenv(gcloud_env["cdsm_google_cred_path"])

        return cdsm_google_cred_path

    def set_storage_object(self):
        """

        :return:
        """
        # Build up storage
        storage_type = self._determine_storage()
        if storage_type == "AWS":
            credentials_dict = self._build_aws_storage_creds()
            storage_obj = S3Store(credentials_dict, self.project_id)
        elif storage_type == "GCloud":
            credentials_path = self._build_gcloud_creds()
            storage_obj = GCloudStore(credentials_path, self.project_id)
        else:
            # Local persistor goes here
            storage_obj = None

        return storage_obj


ins = InitializationService("/Users/mo/Desktop/mineai/Cloud Runner Extras/configs/config",
                            project_id="edys")
