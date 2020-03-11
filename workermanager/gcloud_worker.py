import math
import os
import time
import uuid

from google.oauth2 import service_account

from servicecommon.ssh_utils import ssh_exec_cmd
from workermanager.woker_utils import memstr_to_int, persist_essential_configs, run_command, \
    insert_script_into_startup_script


class GCloudWorkerManager:
    """
    This class is used to manage GCloud Workers for
    a specific project.
    """

    def __init__(self, project_id, experiment_id, worker_dict):
        """
        This class sets up a worker manager given the
        config dictionary.
        :param project_id: Id of the project
        :param worker_dict: Config for the workers
        """
        self.cloud_dsm_base_path = os.path.join(os.path.expanduser("~"), ".mineai")

        # key_name = "ssh_gcloud"
        # self.key_path = os.path.join(self.cloud_dsm_base_path, key_name)

        self._credentials = None
        self._google_project_id = None
        self.experiment_id = experiment_id
        self._username = None

        self._zone = None
        self.project_id = project_id
        self.worker_dict = worker_dict
        self.compute_client = self.connect()

        self.instances = []

    def _execute_gcloud_cmd_association(self, credential_path, project_name):
        """

        :return:
        """
        command = f'gcloud auth activate-service-account ' \
                  f'--key-file="{credential_path}" --project="{project_name}"'
        run_command(command)

    def _initialize_credentials(self):
        """
        This function initializes the credentials
        for GCloud workers into the class variable.
        :returns credentials: Credential Path
        """
        credentials_path = self.worker_dict["env"]. \
            get("cdsm_compute_cred_path")
        self._zone = self.worker_dict["zone"]
        self._credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self._google_project_id = self._credentials._project_id

        self._execute_gcloud_cmd_association(credentials_path,
                                             self._google_project_id)

    def _add_ports(self, port_mapping):
        """

        :param port_mapping: Dictionary containing Protocol:Port mapping
        :return:
        """
        # Get default firewall nodes
        command = 'gcloud compute firewall-rules list --format="table(name)"'
        _, output, _ = run_command(command)
        rules = output.split()[1:]

        # Add Docker Swarm ports
        port_mapping[2376] = "tcp"
        port_mapping[2377] = "tcp"
        port_mapping[7946] = "tcp"
        port_mapping[7946] = "udp"
        port_mapping[4789] = "udp"

        if self.project_id in rules:
            action = "update"
        else:
            action = "create"
        base_command = f"gcloud compute firewall-rules {action} {self.project_id} --allow="
        for port in port_mapping:
            protocol = port_mapping[port]
            base_command += f"{protocol}:{port},"

        base_command = base_command[:-1]

        run_command(base_command)

    def connect(self):
        """
        This function establishes a boto3 client
        and resource object and connects using the
        credentials dict.
        :returns compute_client: The compute client object
        """
        import googleapiclient.discovery
        self._initialize_credentials()
        compute_client = googleapiclient.discovery.build('compute', 'v1',
                                                         credentials=self._credentials)
        return compute_client

    def _stop_instance(self, worker_id, blocking=True):
        """
        This function stops the given worker.
        :param worker: Id/Obj of the worker to be stopped
        :param blocking: Wait for it to stop.
        :returns:
        """
        op = self.compute_client.instances().delete(
            project=self._google_project_id,
            zone=self._zone,
            instance=worker_id).execute()

        if blocking:
            self._wait_for_operation(op['name'])
        else:
            return op['name']

    def _construct_startup_script(self, user_scripts=None, type="worker"):
        """
        This function is used to construct the startup script.
        :param user_script: Location of user startup script
        :return startup_script: Startup script content as
        a byte stream
        """
        # print("##################### Startup Script ##################### \n")
        base_startup_script_path = os.path.join(os.getcwd(),
                                                "worker/base_startup_installation.sh")

        with open(base_startup_script_path) as f:
            base_startup_script = f.read()

        metadata_fetch = os.path.join(os.getcwd(),
                                      "shellscripts/gcloud/get_meta_information.sh")
        python_script_path = os.path.join(os.getcwd(),
                                          "shellscripts/shared/python3.7_install.sh")
        cloud_dsm_clone_path = os.path.join(os.getcwd(),
                                            "shellscripts/shared/cloud_runner_git_clone.sh")
        docker_installation = os.path.join(os.getcwd(),
                                           "shellscripts/shared/docker_installation.sh")



        startup_script = insert_script_into_startup_script(metadata_fetch, base_startup_script)
        startup_script = insert_script_into_startup_script(docker_installation, startup_script)
        startup_script = insert_script_into_startup_script(python_script_path, startup_script)
        startup_script = insert_script_into_startup_script(cloud_dsm_clone_path, startup_script)

        if type == "worker":
            queue_initializer = os.path.join(os.getcwd(),
                                             "shellscripts/shared/start_queue_subscriber.sh")
            startup_script = insert_script_into_startup_script(queue_initializer, startup_script)

        if user_scripts is not None:
            for user_script in user_scripts:
                startup_script = insert_script_into_startup_script(user_script, startup_script)

        # print(startup_script)

        # print("##################### End Script ##################### \n")

        return startup_script

    def _generate_instance_name(self, type):
        """
        This function generates a unique ID for the worker attached with
        the project.
        :returns: A unique instance Id
        """
        return self.project_id + "-" + str(uuid.uuid4()) + "-" + type

    def reset_connection(self, worker_dict, reset_instances=True,
                         shutdown_instances=True):
        """
        This function resets the connection account
        associated with this class
        :param worker_dict: Dictionary of the worker config
        :param reset_instances: If this is set to True, all
        track of instances is removed.
        :param shutdown_instances: If this is set to True,
        all of these instances are shutdown and the track is
        removed as well.
        :returns nothing:
        """
        if reset_instances:
            self.instances = []

        if shutdown_instances:
            self.shutdown()

        self.worker_dict = worker_dict
        self.connect()

    def _generate_machine_type(self, resources_needed):
        """
        Thus function generates the machine type based
        on the resources needed.
        :param resources_needed: A dictionary containing the
        machine resource specs.
        :returns machine_type: Type of the machine to be used
        for the instance.
        """
        if not any(resources_needed):
            machine_type = "zones/{}/machineTypes/n1-standard-1".format(
                self._zone)
        else:
            cpus = int(resources_needed['cpus'])

            # Let default ram be 4GB
            default_ram_per_cpu = 4096

            # GCloud assigns ram per CPU. Thus calculate
            # total ram.
            ram = default_ram_per_cpu * cpus

            # If the user has specified ram
            if 'ram' in resources_needed.keys():
                ram = memstr_to_int(resources_needed['ram']) / memstr_to_int('1Mb')
                ram = int(math.ceil(ram / 256.0) * 256)

            ram_per_cpu = ram / cpus
            assert 1024 <= ram_per_cpu and ram_per_cpu <= 6192, \
                "RAM per cpu should be between 0.9 and 6.5 Gb"

            machine_type = "zones/{}/machineTypes/custom-{}-{}".format(
                self._zone, cpus, ram)

        return machine_type

    def _run_remote_command(self, command, username, instance_name):
        """

        :param command:
        :return:
        """
        remote_command = f"gcloud compute ssh {username}@{instance_name} --zone={self._zone} --command='{command}'"
        run_command(remote_command)

    def _scp_files(self, worker_name, local_file_path,
                   instance_file_path, username):
        """
        This function copies the file path.
        :param worker_name: Name of the worker
        :param local_file_path: File Path on the localhost
        :return nothing:
        """
        command = f"gcloud compute scp --recurse " \
                  f"{local_file_path} {username}@{worker_name}:{instance_file_path} " \
                  f"--zone={self._zone}"
        run_command(command)

    def _scp_configs(self, worker_name, local_file_path,
                     instance_file_path, username):

        self._scp_files(worker_name, local_file_path,
                        instance_file_path, username)
        mkdir_command = f"sudo mkdir -p /.mineai"
        self._run_remote_command(mkdir_command, username, worker_name)

        copy_command = f"sudo mv {instance_file_path} /.mineai/configs"
        self._run_remote_command(copy_command, username, worker_name)

    def _generate_instance_config(self, resources_needed,
                                  queue_config, storage_config, user_scripts, type="worker"):
        """

        :return:
        """
        # Check if the user specified the image
        if "image_specs" in self.worker_dict.keys():
            image_specs = self.worker_dict["image_specs"]
            image_project = image_specs["project"]
            family = image_specs["family"]
        else:
            image_project = 'gce-uefi-images'
            family = 'ubuntu-1804-lts'

        # Generate the Image
        image_response = self.compute_client.images().getFromFamily(
            project=image_project, family=family).execute()
        source_disk_image = image_response['selfLink']

        # Generate
        machine_type = self._generate_machine_type(resources_needed=resources_needed)

        startup_script = self._construct_startup_script(user_scripts, type)

        configs_local_path = os.path.join(self.cloud_dsm_base_path, "configs")
        configs_local_path = os.path.abspath(configs_local_path)
        persist_essential_configs({
            "config": queue_config,
            "filename": "queue_config"
        },
            {
                "config": storage_config,
                "filename": "storage_config"
            },
            persist_path=configs_local_path)

        with open(f"{configs_local_path}/queue_config.json") as f:
            queue_config_byte_str = f.read()
        with open(f"{configs_local_path}/storage_config.json") as f:
            storage_config_byte_str = f.read()
        with open(f"{configs_local_path}/completion_service_queue_config.json") as f:
            completion_service_queue_config_byte_str = f.read()
        with open(f"{configs_local_path}/completion_service_storage_config.json") as f:
            completion_service_storage_config_byte_str = f.read()

        config = {
            # 'user-name': "ubuntu",
            'machineType': machine_type,

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    }
                }
            ],

            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ],
            }],

            # Allow the instance to access cloud storage and logs.
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                    'https://www.googleapis.com/auth/cloud-platform',
                ]
            }],

            # Metadata is readable from the instance and allows you to
            # pass configuration from deployment scripts to instances.
            'metadata': {
                'items': [{
                    'key': 'startup-script',
                    'value': startup_script
                }, {
                    'key': 'queue-config',
                    'value': queue_config_byte_str
                }, {
                    'key': 'storage-config',
                    'value': storage_config_byte_str
                }, {
                    'key': 'completion-service-queue-config',
                    'value': completion_service_queue_config_byte_str
                }, {
                    'key': 'completion-service-storage-config',
                    'value': completion_service_storage_config_byte_str
                }]
            },
            "scheduling": {
                "preemptilble": False
            }
        }

        if 'hdd' in resources_needed.keys():
            config['disks'][0]['initializeParams']['diskSizeGb'] = \
                memstr_to_int(resources_needed['hdd']) / memstr_to_int('1Gb')

        if resources_needed['gpus'] > 0:
            gpu_type = "nvidia-tesla-k80" or \
                       resources_needed.get("gpu_type", None)
            config['guestAccelerators'] = [
                {
                    "acceleratorType":
                        "projects/{}/zones/{}/acceleratorTypes/{}"
                            .format(self._google_project_id,
                                    self._zone, gpu_type),
                    "acceleratorCount": resources_needed['gpus']
                }
            ]

            config["scheduling"]['onHostMaintenance'] = "TERMINATE"
            config["automaticRestart"] = True

        return config

    def get_worker(self, worker_name):
        """
        This funciton fetches the workers on this project
        :return:
        """
        workers = self.get_workers()
        queried_worker = None
        for worker in workers:
            if worker["name"] == worker_name:
                queried_worker = worker

        return queried_worker

    def get_workers(self):
        """
        This funciton fetches the workers on this project
        :return:
        """
        result = self.compute_client. \
            instances().list(project=self._google_project_id,
                             zone=self._zone).execute()
        return result['items'] if 'items' in result else None

    def _get_worker_ip(self, worker_name):
        """
        This function fetches the public IP Address
        of the instance.
        :param worker_name:
        :return:
        """
        worker = self.get_worker(worker_name)
        worker_ip = worker["networkInterfaces"][0]['accessConfigs'][0]['natIP']
        return worker_ip

    def start_worker(self, queue_config, storage_config, resources_needed=None, blocking=True,
                     ssh_keypair=None, timeout=300, ports=None, name=None, user_scripts=None, type="worker"):
        """
        This function is used to start EC2 the instance on AWS.
        :param queue_config: Queue Config
        :param storage_config: Storage Config
        :param resources_needed: Dictionary of the resources
        :param blocking: Wait until instance has booted up
        :param ssh_keypair: Keypair Dict to grant SSH Access.
        The filename without the .pem extension
        :param timeout:
        :param ports: Ports that need to be assigned.
        :param name: Name to attach to the instance
        :returns nothing:
        """
        if ssh_keypair is not None:
            print('ssh keypairs are not supported ' +
                  'for google workers')
        if resources_needed is None:
            resources_needed = {}

        if name is None:
            name = self._generate_instance_name(type)

        instance_config = self._generate_instance_config(resources_needed, queue_config,
                                                         storage_config, user_scripts, type)
        instance_config['name'] = name

        op = self.compute_client.instances().insert(
            project=self._google_project_id,
            zone=self._zone,
            body=instance_config).execute()

        if blocking:
            self._wait_for_operation(op['name'])
            print('worker {} created'.format(name))

            self.instances = self.get_workers()

            port_map = {}
            for port in ports:
                port_map[port] = "tcp"

            self._add_ports(port_map)

            # Hold until Docker is installed
            ip_addr = self._get_worker_ip(name)

            current_user_path = os.path.expanduser("~")
            key_pair_path = os.path.join(current_user_path, ".ssh/google_compute_engine")

            print("Waiting for Docker to be installed")
            installed = False
            while not installed:
                command = "sudo docker"
                _, ssh_stdout, ssh_stderr = ssh_exec_cmd(hostname=ip_addr,
                                                         username="ubuntu",
                                                         key_filepath=key_pair_path, command=command)
                out, err = ssh_stdout.read().splitlines(), \
                           ssh_stderr.read().splitlines()
                installed = len(err) > 1
                from time import sleep
                sleep(5)


            if type == "master":
                print("Initializing Master .... ")
                master_initialized = False
                while not master_initialized:
                    try:
                        command = f"sudo docker swarm init --advertise-addr {ip_addr}"
                        _, _, _ = ssh_exec_cmd(hostname=ip_addr,
                                               username="ubuntu",
                                               key_filepath=key_pair_path, command=command)

                        command = f"sudo docker swarm join-token worker"

                        _, ssh_stdout, ssh_stderr = ssh_exec_cmd(hostname=ip_addr,
                                                                 username="ubuntu",
                                                                 key_filepath=key_pair_path, command=command)

                        token_lines = ssh_stdout.read().splitlines()
                        token = token_lines[-2].decode().strip()
                        master_initialized = True
                        print("Master Setup complete..")
                        break
                    except Exception as e:
                        print(e)
                        continue

                master_token_path = os.path.join(self.cloud_dsm_base_path,
                                                 f"{self.project_id}/{self.experiment_id}")
                if not os.path.exists(master_token_path):
                    os.makedirs(master_token_path)
                with open(os.path.join(master_token_path, "master_node_connect_token.txt"), 'w') as f:
                    f.write(token)

            elif type == "worker":
                print("Connecting Worker to Master .... ")
                master_token_path = os.path.join(self.cloud_dsm_base_path,
                                                 f"{self.project_id}/{self.experiment_id}")
                with open(os.path.join(master_token_path, "master_node_connect_token.txt"), 'r') as f:
                    command = f.read()

                command = f"sudo {command}"

                _, ssh_stdout, ssh_stderr = ssh_exec_cmd(hostname=ip_addr,
                                                         username="ubuntu",
                                                         key_filepath=key_pair_path, command=command)

                swarm_join_response = ssh_stdout.read().splitlines()
                swarm_join_error = ssh_stderr.read().splitlines()
                print(f"Swarm Join Out: {swarm_join_response}")
                print(f"Swarm Join Error: {swarm_join_error}")

    def create_workers(self, queue_config, storage_config):
        """
        This function is used to start EC2 the instance on AWS.
        :param storage_config:
        :param queue_config: Queue Config
        :param blocking: Wait until instance has booted up
        :param ssh_keypair: Keypair to grant SSH Access.
        The filename without the .pem extension
        :param timeout:
        :param ports: Ports that need to be assigned.
        :returns nothing:
        """
        resources_needed = self.worker_dict["resources"]
        num_workers = resources_needed.get("num_workers", 1)
        user_scripts = self.worker_dict.get("user_scripts", None)
        blocking = True
        ssh_keypair = self.worker_dict.get("ssh_keypair", None)
        timeout = self.worker_dict.get("timeout", 300)
        ports = self.worker_dict.get("ports", None)

        for _ in range(num_workers):
            self.start_worker(queue_config, storage_config, resources_needed, blocking,
                              ssh_keypair, timeout, ports, user_scripts=user_scripts)

    def _wait_for_operation(self, operation):
        """
        This function halts the instance creation
        function from exiting until the operation
        is finished
        :param operation:
        :return:
        """
        print('Waiting for operation {} to finish...'.
              format(operation))
        while True:
            result = self.compute_client.zoneOperations().get(
                project=self._google_project_id,
                zone=self._zone,
                operation=operation).execute()

            if result['status'] == 'DONE':
                print("done.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result

            time.sleep(1)
