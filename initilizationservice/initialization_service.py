from initilizationservice.config_handler import ConfigHandler
from queuingservices.managers.queue_master import QueueMaster
from storage.storage_creator import StorageCreator
from workermanager.aws_worker import EC2WorkerManager
from workermanager.gcloud_worker import GCloudWorkerManager
from workermanager.woker_utils import persist_essential_configs, run_command

import os
import copy
import uuid


class InitializationService:

    def __init__(self, project_name, username, config_path):
        """
        The constructor initializes the config file, the project
        and the user name.
        :param project_name: Project name to be assigned
        :param username: Username to be attached to this project.
        This will later on be used for security purposes
        :param config_path: Path of the config
        """
        config_parser = ConfigHandler(config_path, project_name=project_name)
        self.compute_config = config_parser.get_compute_config()
        self.storage_config = config_parser.get_storage_config()
        self.queue_config = config_parser.get_queue_config()
        self.master_node_config = config_parser.get_master_node_config()

        self.project_name = project_name
        self.username = username
        self.experiment_id = uuid.uuid4()

        storage_creator = StorageCreator(self.storage_config)
        self.storage_object = storage_creator.build_storage_object()

        self.cloud_runner_base_path = os.path.join(os.path.expanduser("~"), ".mineai")
        self.config_path = os.path.join(self.cloud_runner_base_path, "configs")

        self.completion_service_queue_config = copy.deepcopy(self.queue_config)
        if self.completion_service_queue_config["type"] == "rmq":
            self.completion_service_queue_config["exchange_name"] = f"mine_ai_{project_name}_completion_service"
        elif self.completion_service_queue_config["type"] == "sqs":
            if "queue_url" in self.completion_service_queue_config:
                del self.completion_service_queue_config["queue_url"]
        self.completion_service_queue_config["queue_name"] = f"mine_ai_{project_name}_completion_service"

        persist_essential_configs({
            "config": self.completion_service_queue_config,
            "filename": "completion_service_queue_config"
        },
            {
                "config": self.storage_config,
                "filename": "completion_service_storage_config"
            },
            persist_path=self.config_path)

        self.initialize_queue()
        # self.completion_service_process = self.initialize_completion_service()

        self.compute_managers = {}
        self.create_instances()

    def initialize_completion_service(self):
        """
        This function spins up the completion service to
        listen for events and fetch back the results of the jobs.
        :returns nothing:
        """
        queue_config_path = f"{self.config_path}/completion_service_queue_config.json"
        storage_config_path = f"{self.config_path}/completion_service_storage_config.json"

        command = f"python -m completionservice.completion_service --queue_config_path={queue_config_path} " \
                  f"--storage_config_path={storage_config_path} --project_name={self.project_name}"
        _, complete_output, process = run_command(command, False)
        print(f"Completion Service PID: {process.pid}")
        return process

    def _create_completion_submission_docker_compose(self):
        """

        :return:
        """
        docker_compse_dict = {
            "version": "3.7",

        }

    def initialize_queue(self):
        """
        This function creates the queues required fi they don't
        already exist.
        :return nothing:
        """
        queue_master = QueueMaster(self.queue_config)
        queue_lifecycle_object = queue_master.build_lifecycle_object()
        queue_lifecycle_object.create_queue(self.queue_config["queue_name"])
        queue_lifecycle_object.create_queue(self.completion_service_queue_config["queue_name"])

    def _create_master_node(self):
        if self.master_node_config is None:
            import random
            master_node_provider = random.choice(list(self.compute_config.keys()))
            print("Master Node hosted On: ", master_node_provider)
            compute_type_config = self.compute_config[master_node_provider]
        else:
            master_node_provider = self.master_node_config.get("type")
            compute_type_config = self.master_node_config

        resources_needed = compute_type_config["resources"]
        user_scripts = compute_type_config.get("user_scripts", None)
        blocking = True
        ssh_keypair = compute_type_config.get("ssh_keypair", None)
        timeout = compute_type_config.get("timeout", 300)
        ports = compute_type_config.get("ports", None)

        if master_node_provider in ["aws", "ec2"]:
            compute_obj = EC2WorkerManager(self.project_name, self.experiment_id, compute_type_config)

        elif master_node_provider == "gcloud":
            compute_obj = GCloudWorkerManager(self.project_name, self.experiment_id, compute_type_config)

        compute_obj.start_worker(self.queue_config, self.storage_config, resources_needed, blocking,
                                 ssh_keypair, timeout, ports, user_scripts, type="master")

    def create_instances(self):
        """
        This function initializes the instances.
        :returns nothing:
        """

        self._create_master_node()

        for compute_type in self.compute_config.keys():
            compute_type_config = self.compute_config[compute_type]
            if compute_type in ["aws", "ec2"]:
                compute_obj = EC2WorkerManager(self.project_name, self.experiment_id, compute_type_config)
                compute_obj.create_workers(self.queue_config, self.storage_config)
                self.compute_managers[compute_type] = compute_obj
            elif compute_type == "gcloud":
                compute_obj = GCloudWorkerManager(self.project_name, self.experiment_id, compute_type_config)
                compute_obj.create_workers(self.queue_config, self.storage_config)
                self.compute_managers[compute_type] = compute_obj


ins = InitializationService(config_path="/Users/mo/Desktop/mineai/Cloud Runner Extras/configs/config",
                            username="mohak.kant",
                            project_name="cluster-test")
