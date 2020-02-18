import calendar
import time
import os


# put imports from other python classes here
from fstracker.fs_tracker import FileSystemTracker
from servicecommon.parsers.config_parser import ConfigParser
from servicecommon.persistor.cloud.aws.s3_store import S3Store
from servicecommon.persistor.cloud.gcloud.gcloud_store import GCloudStore
from services.queuingservices.job_struct import JobStruct
from services.queuingservices.rabbitmq.task_submit import TaskSubmit


class SubmissionService:

    def __init__(self, config_path, project_id):
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

    def create_queue_submittor(self, queue_name=None):
        """

        :param queue_name:
        :return:
        """
        exchange_name = self.queue_config.get("exchange_name")
        endpoint = self.queue_config.get("endpoint")
        task_submittor = TaskSubmit(queue_name, exchange_name, endpoint)
        task_submittor.establish_connection()

        return task_submittor

    def _determine_storage(self):
        """

        :return:
        """
        storage_type = self.storage_config.get("type")
        if storage_type in ("s3", "minio"):
            return "aws"
        elif storage_type in ("gcloud"):
            return "gcloud"
        else:
            return "local"

    def _build_aws_creds(self):
        """

        :return:
        """
        aws_env = self.storage_config.get("env")
        cdsm_aws_access_key = os.getenv(aws_env["cdsm_aws_access_key"])
        cdsm_aws_secret_key = os.getenv(aws_env["cdsm_aws_secret_key"])

        if not cdsm_aws_access_key:
            cdsm_aws_access_key = "minioadmin"
            cdsm_aws_secret_key = "minioadmin"

        credentials_dict = {
            "access_key": cdsm_aws_access_key,
            "secret_key": cdsm_aws_secret_key,
            "endpoint_url": self.storage_config.get("endpoint_url"),
            "region": self.storage_config.get("region")
        }

        return credentials_dict

    def _build_gcloud_creds(self):
        """

        :return:
        """
        gcloud_env = self.storage_config.get("env")
        cdsm_google_cred_path = os.getenv(gcloud_env["cdsm_google_cred_path"])

        if cdsm_google_cred_path is None:
            cdsm_google_cred_path = \
                "/Users/mo/Desktop/mineai/CloudRunner/my-project1-254915-805e652a60d3.json"

        return cdsm_google_cred_path

    def set_storage_object(self):
        """

        :return:
        """
        # Build up storage
        storage_type = self._determine_storage()
        if storage_type == "aws":
            credentials_dict = self._build_aws_creds()
            storage_obj = S3Store(credentials_dict)
        elif storage_type == "gcloud":
            credentials_path = self._build_gcloud_creds()
            storage_obj = GCloudStore(credentials_path)
        else:
            # Local persistor goes here
            storage_obj = None

        return storage_obj

    def submit_task(self, payload_path, queue_name,
                    job_id=None):
        """

        This function will start a task, add it to the queue of tasks, and store the reference information
        in a cloud or local environment.

        :param payload_path:
        :param queue_name:
        :param task_id:
        :return:
        """

        # Create Job ID
        if job_id is None:
            job_id = SubmissionService.generate_task_id()

        # Tar and store job data
        temp_path = f"../../temp/{self.project_id}/{job_id}"
        fs_tracker = FileSystemTracker(payload_path,
                                       temp_path,
                                       self.storage_obj,
                                       project_name=self.project_id,
                                       job_id=job_id)
        fs_tracker.persist()

        # Build the job description
        job_message = JobStruct(storage_config=self.storage_config,
                                bucket_name=self.project_id,
                                experient_id=job_id).__dict__

        # Add the task ID to the Queue
        task_submittor = self.create_queue_submittor(queue_name)
        task_submittor.submit(job_message)

    def submit_task_with_data(self, payload_path, data_path, queue_name, task_id=None):
        """

                This function will start a task, add it to the queue of tasks, and store the reference information
                in a cloud or local environment.

                :param data_path:
                :param payload_path:
                :param queue_name:
                :param task_id:
                :return:
                """

        if task_id is None:
            task_id = SubmissionService.generate_task_id()

        # Add the task ID to the Queue
        task_obj = TaskSubmit(queue_name, task_id)
        task_obj.submit()

        # Store the payload path with corresponding task ID in a location

    @staticmethod
    def generate_task_id(base_word=None):
        """

        This function will generate a task id with a given or default base word


        :param base_word: an optional argument if you wanted a specific word for your task. It defaults to 'task'
        :return: task_id: unique string generated for each task submitted
        """

        # check to see if you should add the default base word
        if base_word is None:
            base_word = "task"

        # generate a number
        id_number = calendar.timegm(time.gmtime())

        # assemble the task id
        task_id = f"{base_word}_{id_number}"

        return task_id


