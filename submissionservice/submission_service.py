import calendar
import time

# put imports from other python classes here
from services.queuingservices.rabbitmq.task_submit import TaskSubmit


class SubmissionService:

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None

    def connect_to_queue(self, queue_name=None):
        pass

    def submit_task(self, payload_path, queue_name, task_id=None):
        """

        This function will start a task, add it to the queue of tasks, and store the reference information
        in a cloud or local environment.

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
