from initilizationservice.config_handler import ConfigHandler
from queuingservices.managers.queue_master import QueueMaster
from storage.job_storage_interface import JobStorageInterface
from storage.storage_creator import StorageCreator
from utils import export_env_variable, persist_essential_configs, \
    run_command, generate_big_random_bin_file, \
    generate_timestamp
from workermanager.aws_worker import EC2WorkerManager
from workermanager.gcloud_worker import GCloudWorkerManager

import os
import copy
from logzero import logger

DEFAULT_BASE_DIR = os.path.join(os.path.expanduser("~"),
                                ".mineai/cloud_runner")
DEFAULT_BUCKET_NAME = "mine-ai"
PYTHON_VERSION = "3.7"


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
        config_parser = ConfigHandler(config_path,
                                      project_name=project_name)
        self.compute_config = config_parser.get_compute_config()
        self.storage_config = config_parser.get_storage_config()
        self.queue_config = config_parser.get_queue_config()
        self.master_node_config = config_parser.get_master_node_config()
        self.compute_ports = config_parser.get_ports()

        self.project_name = project_name
        self.username = username
        self.experiment_id = generate_timestamp("experiment")
        logger.info(f"Experiment ID: {self.experiment_id}\n")

        self.experiment_dir = self.initialize_folders()
        self._initialize_bucket_structure()
        self.initialize_queue()

        self._create_completion_submission_docker_compose()

        self.completion_service_process = \
            self.initialize_completion_service()

        self.compute_managers = {}
        self.create_instances()

    def _initialize_bucket_structure(self):
        """
        This function creates the base structure for the
        bucket regarding this experiment.
        """
        storage_creator = StorageCreator(self.storage_config)
        storage_object = storage_creator.build_storage_object()

        # Dump some test data
        FILE_TEST_SIZE = int(5e6)  # Approx 5MB
        MAX_RETRIES = 2
        retries = 0
        file_path = os.path.join(self.experiment_dir,
                                 "initialization-service-test")
        generate_big_random_bin_file(file_path, FILE_TEST_SIZE)

        while retries < 2:
            # Perform Storage Connection Test
            logger.info("####### Testing Connection to Storage Endpoint ....")
            storage_object.create_bucket(DEFAULT_BUCKET_NAME)
            try:
                storage_interfacer = JobStorageInterface(storage_obj=storage_object)
                storage_interfacer.put_job_data(bucket=DEFAULT_BUCKET_NAME,
                                                username=self.username,
                                                project_id=self.project_name,
                                                experiment_id=self.experiment_id,
                                                variant="Initialization Service",
                                                job_id="inital_testing",
                                                local_path=file_path)
                logger.info("File Upload to Storage Endpoint Succeeded....")
                break
            except ConnectionError as e:
                logger.error("File Upload failed, please check to storage config ....\m"
                             f"{e}")

                if retries == MAX_RETRIES - 1:
                    import sys
                    logger.critical("\nProblem connecting to Storage. Exiting")
                    sys.exit(status="Problem connecting to Storage. Exiting")
                else:
                    logger.error(f"Trying to reconnect. {MAX_RETRIES - retries} remaining")
                    retries += 1
                    continue

        file_path = os.path.join(self.experiment_dir, "initialization-service-test_restore")
        try:
            storage_interfacer.get_job_data(bucket=DEFAULT_BUCKET_NAME,
                                            username=self.username,
                                            project_id=self.project_name,
                                            experiment_id=self.experiment_id,
                                            variant="Initialization Service",
                                            job_id="inital_testing",
                                            local_path=file_path)
            logger.info("File Download from Storage Endpoint Succeeded....")
        except ConnectionError as e:
            logger.warning("File Download failed, connection might be unstable ....\m"
                           f"{e}")

    def initialize_folders(self):
        """
        This function sets up the basic project structure.
        """
        # Export location of base directory.
        export_env_variable(name="MINE_AI_CLOUD_RUNNER_BASE_DIR",
                            value=DEFAULT_BASE_DIR)

        # Initialize Base Directory
        if not os.path.exists(DEFAULT_BASE_DIR):
            os.makedirs(DEFAULT_BASE_DIR)

        # Initialize Username Director
        username_dir = os.path.join(DEFAULT_BASE_DIR, self.username)

        # Initialize Project Dir
        project_dir = os.path.join(username_dir, self.project_name)

        # Initialize Experiment Dir
        experiment_dir = os.path.join(project_dir, str(self.experiment_id))

        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        return experiment_dir

    def _create_completion_service_queue_config(self):
        """
        This function creates the configs for the completion
        service
        """
        completion_service_queue_config = copy.deepcopy(self.queue_config)
        if completion_service_queue_config["type"] == "rmq":
            completion_service_queue_config["exchange_name"] = f"mine_ai_{self.project_name}_completion_service"
        elif completion_service_queue_config["type"] == "sqs":
            if "queue_url" in completion_service_queue_config:
                del completion_service_queue_config["queue_url"]
        completion_service_queue_config["queue_name"] = f"mine_ai_{self.project_name}_completion_service"

        return completion_service_queue_config

    def initialize_completion_service(self):
        """
        This function spins up the completion service to
        listen for events and fetch back the results of the jobs.
        :returns process: The process managing the Completion Service
        """
        completion_service_queue_config = \
            self._create_completion_service_queue_config()
        config_path = os.path.join(self.experiment_dir, "configs")
        persist_essential_configs({
            "config": completion_service_queue_config,
            "filename": "completion_service_queue_config"
        },
            {
                "config": self.storage_config,
                "filename": "completion_service_storage_config"
            },
            persist_path=config_path)

        queue_config_path = os.path.join(config_path, "completion_service_queue_config.json")
        storage_config_path = os.path.join(config_path, "completion_service_storage_config.json")

        command = f"python -m completionservice.completion_service --queue_config_path={queue_config_path} " \
                  f"--storage_config_path={storage_config_path} --project_name={self.project_name}"
        _, complete_output, process = run_command(command, False)
        print(f"Completion Service PID: {process.pid}")
        return process

    def _create_completion_submission_docker_compose(self):
        """
        This function persists the docker compose yaml
        """
        python_image = f"{PYTHON_VERSION}-stretch"
        worker_mineai_dir = "/.mineai"
        worker_config_dir = "/.mineai"
        docker_compose_dict = {
            "version": "3.7",
            "services": {
                "subscriber": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile",
                        "args":
                            [
                                f"PYTHON_IMAGE_VERSION={python_image}"
                            ],
                        "environment":
                            [
                                f"BASE_CONFIG_PATH={worker_mineai_dir}"
                            ]
                    },
                    "ports": [],
                    "expose": [],
                    "volumes": [
                        f"{worker_config_dir}:{worker_config_dir}"
                    ],
                    "restart": "always",
                    "tty": True
                },

            }
        }
        ports = self.compute_ports
        for port in ports:
            docker_compose_dict["services"]["subscriber"]["ports"].append(f"{port}:{port}")
            docker_compose_dict["services"]["subscriber"]["expose"].append(port)

        import yaml
        with open('services/worker_completion_submission_service/docker-compose.yml', 'w') as outfile:
            yaml.dump(docker_compose_dict, outfile, default_flow_style=False)

    def initialize_queue(self):
        """
        This function creates the queues required fi they don't
        already exist.
        :return nothing:
        """
        queue_master = QueueMaster(self.queue_config)
        queue_lifecycle_object = queue_master.build_lifecycle_object()
        queue_lifecycle_object.create_queue(self.queue_config["queue_name"])
        completion_service_queue_config = \
            self._create_completion_service_queue_config()
        queue_lifecycle_object.create_queue(completion_service_queue_config["queue_name"])

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
            compute_obj = EC2WorkerManager(self.project_name,
                                           self.experiment_id,
                                           compute_type_config,
                                           self.experiment_dir,
                                           logger)

        elif master_node_provider == "gcloud":
            compute_obj = GCloudWorkerManager(self.project_name,
                                              self.experiment_id,
                                              compute_type_config,
                                              self.experiment_dir,
                                              logger)

        compute_obj.start_worker(self.queue_config, self.storage_config, resources_needed, blocking,
                                 ssh_keypair, timeout, ports, user_scripts, type="master")

    def create_instances(self):
        """
        This function initializes the instances.
        :returns nothing:
        """
        self._create_master_node()

        from multiprocessing import Process
        processes = []
        for compute_type in self.compute_config.keys():
            compute_type_config = self.compute_config[compute_type]
            if compute_type in ["aws", "ec2"]:
                compute_obj = EC2WorkerManager(self.project_name,
                                               self.experiment_id,
                                               compute_type_config,
                                               self.experiment_dir,
                                               logger)


            elif compute_type == "gcloud":
                compute_obj = GCloudWorkerManager(self.project_name,
                                                  self.experiment_id,
                                                  compute_type_config,
                                                  self.experiment_dir,
                                                  logger)

            process = Process(target=compute_obj.create_workers,
                             args=(self.queue_config,
                                   self.storage_config))
            processes.append(process)
            # compute_obj.create_workers(self.queue_config,
            #                            self.storage_config)
            self.compute_managers[compute_type] = compute_obj

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        logger.info("Cluster Successfully Created")


ins = InitializationService(config_path="/Users/mo/Desktop/mineai/Cloud Runner Extras/configs/config",
                            username="mohak.kant",
                            project_name="cluster-test")
