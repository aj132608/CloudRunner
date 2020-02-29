import calendar
import time

from fstracker.fs_tracker import FileSystemTracker
from servicecommon.parsers.config_parser import ConfigParser
from queuingservices.job_struct import JobStruct
from queuingservices.rabbitmq.publisher import Publisher


class SubmissionService:

    def __init__(self, config_path, project_id,
                 initialization_service_object=None):
        """

        :param config_path:
        """
        self.config_path = config_path
        self.config_parser = ConfigParser(self.config_path)
        self.project_id = project_id

        self.computes = self.config_parser.get_computing_environments()
        self.storage_config = self.config_parser.get_storage_config()


    def create_queue_submitter(self, queue_name=None):
        """

        :param queue_name:
        :return:
        """
        exchange_name = self.queue_config.get("exchange_name")
        endpoint = self.queue_config.get("endpoint")
        task_submitter = Publisher(queue_name, exchange_name, endpoint)
        task_submitter.establish_connection()

        return task_submitter

    def submit_task(self, payload_path, queue_name,
                    job_id=None):
        """
        This function will start a task, add it to the queuingservices of tasks, and store the reference information
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
                                       project_id=job_id)
        fs_tracker.persist()

        # Build the job description
        job_message = JobStruct(storage_config=self.storage_config,
                                bucket_name=self.project_id,
                                experient_id=job_id).__dict__

        # Add the task ID to the Queue
        task_submittor = self.create_queue_submitter(queue_name)
        task_submittor.submit(job_message)

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


