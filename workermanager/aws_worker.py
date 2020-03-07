import os
import uuid
import boto3
import botocore
import yaml
import hashlib
import pickle

from servicecommon.environment_utils import extract_environment_variables
from servicecommon.scp import scp_send
from workermanager.woker_utils import memstr_to_int, \
    _aws_instance_specs, _get_aws_ondemand_prices, persist_essential_configs


class EC2WorkerManager:
    """
    This class is used to manage EC2 workers
    for a specific project.
    """

    def __init__(self, project_id, worker_dict):
        """
        This class sets up a worker manager given the
        config dictionary.
        :param project_id: Id of the project
        :param worker_dict: Config for the workers
        """
        self.cloud_dsm_base_path = "~/"

        if not os.path.exists(self.cloud_dsm_base_path):
            os.makedirs(self.cloud_dsm_base_path)

        self.project_id = project_id
        self.worker_dict = worker_dict
        self.compute_resource, self.compute_client = \
            self.connect()

        self.instances = []

    def connect(self):
        """
        This function establishes a boto3 client
        and resource object and connects using the
        credentials dict.
        :return:
        """
        resource_name = "ec2"

        env_vars = self.worker_dict.get("env")
        credentials_dict = extract_environment_variables(env_vars)
        credentials_dict["region"] = self.worker_dict.get("region")

        access_key = credentials_dict['cdsm_compute_access_key']
        secret_key = credentials_dict['cdsm_compute_secret_key']
        region = credentials_dict['region']

        compute_resource = boto3.resource(resource_name,
                                          region_name=region,
                                          aws_access_key_id=access_key,
                                          aws_secret_access_key=secret_key)
        compute_client = boto3.client(resource_name,
                                      region_name=region,
                                      aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key)

        return compute_resource, compute_client

    def reset_project(self, project_id, reset_instances=True,
                      shutdown_instances=True):
        """
        This function attaches this worker manager
        to a different project
        :param project_id: The project id
        :returns nothing:
        """
        self.project_id = project_id

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

    def _generate_instance_name(self):
        """
        This function generates a unique ID for the worker attached with
        the project.
        :returns: A unique instance Id
        """
        return self.project_id + "-" + str(uuid.uuid4())

    def _select_instance_type(self, resources_needed):
        """
        This function returns a selected instance type based on
        the resource provided.
        :param resources_needed: Dictionary containing the resource
        needed for the instance
        :return:
        """
        prices = _get_aws_ondemand_prices()
        sorted_specs = sorted(_aws_instance_specs.items(),
                              key=lambda x: prices[x[0]])
        for instance in sorted_specs:
            if int(instance[1]['cpus']) >= int(resources_needed['cpus']) \
                    and memstr_to_int(instance[1]['ram']) >= \
                    memstr_to_int(resources_needed['ram']) \
                    and int(instance[1]['gpus']) >= \
                    int(resources_needed['gpus']):
                return instance[0]

        raise ValueError('No instances that satisfy requirements {} '
                         'can be found'.format(resources_needed))

    def _get_image_id(self, image_type=None):
        """
        TODO: Add Ubuntu 18.04 in aws_amis.yaml
        This function returns an appropriate image
        id based on the region and the
        base image type specified.
        :param image_type: Type of Image (Version of OS)
        :returns: String containing the image id
        """
        price_path = os.path.join(
            os.path.dirname(__file__),
            'aws_amis.yaml')
        with open(price_path) as f:
            ami_dict = yaml.load(f.read())

        region = self.compute_client._client_config.region_name
        image_type = image_type or 'ubuntu16.04'
        return ami_dict[image_type][region]

    def _get_block_device_mappings(self, resources_needed):
        """
        This function generates a blocking for Volume Size
        on the instance
        :param resources_needed: Dictionary containing the
        resources
        :return blocking_config: Config regarding the Volume
        size of the hard disk space.
        """
        blocking_config = [{
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': int(memstr_to_int(resources_needed['hdd']) /
                                  memstr_to_int('1g')),
                'VolumeType': 'standard'
            }
        }]
        return blocking_config

    def _get_security_group(self, ports):
        """
        This function creates the security group
        required (if any) for the desired configuration
        :param ports: List containing the port numbers
        :returns groupid: Id of the group created on AWS
        """
        ports = sorted([p for p in set(ports)])
        group_name = f"{self.project_id}_" \
                     f"{hashlib.sha256(pickle.dumps(sorted(ports))).hexdigest()}"

        try:
            response = self.compute_client.describe_security_groups(
                GroupNames=[group_name]
            )
            groupid = response['SecurityGroups'][0]['GroupId']

        except botocore.exceptions.ClientError as e:
            print("Error creating security group!")
            print(e)
            response = self.compute_client.create_security_group(
                GroupName=group_name,
                Description='opens ports {} in MineAI Cloud DSM workers'
                    .format(",".join([str(p) for p in ports]))
            )

            groupid = response['GroupId']

            ip_permissions = []
            for port in ports:
                ip_permissions.append({
                    'IpProtocol': 'tcp',
                    'FromPort': int(port),
                    'ToPort': int(port),
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                    }]
                })

            _ = self.compute_client.authorize_security_group_ingress(
                GroupId=groupid,
                GroupName=group_name,
                IpPermissions=ip_permissions
            )

        return groupid

    def get_instance_status(self, instance):
        """
        This function returns the status
        of an instance
        :param instance: Instance Object/Id
        :returns status: Status of the instance
        """
        if isinstance(instance, str):
            instance = self.get_instance_from_id(instance)

        status = instance.status
        return status

    def get_instance_from_id(self, instance_id):
        """
        This function returns an EC2 instance object
        tied with the instance_id
        :param instance_id:
        :returns instance: Instance describing the
        instance id
        """
        instance = None
        instances_on_ec2 = self.compute_resource. \
            instances.filter(InstanceIds=[instance_id])
        for maybe_instance in instances_on_ec2:
            instance = maybe_instance
            return instance

    def create_key_pair(self, key_name, key_path):
        """
        Creates private key to communicate with EC2 Instance
        """

        create_new_key_val_pair = False
        # call the boto ec2 function to create a key pair
        try:
            # If key_name_already_exists
            self.compute_client.describe_key_pairs(KeyNames=[key_name])

            # Check if we have a .pem file for it
            if os.path.exists(key_path):
                # If we do - do nothing
                print("Using existing Key Value Pair")
                return
            else:
                # If we do not have the .pem file but an existing
                # key name
                print("Deleting Old. Creating new Key Value Pair")
                self.compute_client.delete_key_pair(KeyName=key_name)
                create_new_key_val_pair = True

        except:
            print("Creating new Key Value Pair")
            create_new_key_val_pair = True

        if create_new_key_val_pair:
            # create a file to store the key locally
            outfile = open(key_path, 'w')

            # If we do not create a new key pair
            key_pair = self.compute_resource.create_key_pair(KeyName=key_name)

            # capture the key and store it in a file
            key_pair_out = str(key_pair.key_material)
            outfile.write(key_pair_out)
            outfile.close()

    def restart_instance(self, instance):
        """

        :param instance:
        :return:
        """
        if isinstance(instance, str):
            instance = self.get_instance_from_id(instance)
        instance.restart()

    def start_worker(self, queue_config, storage_config, resources_needed=None, blocking=True,
                     ssh_keypair=None, timeout=300, ports=None, name=None, image_specs=None):
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
        if ports is None:
            ports = [22]
        if resources_needed is None:
            resources_needed = {}

        # Check if Image Specs are specified
        if image_specs is not None:
            image_type = image_specs["image_type"] # More like Version of OS
        else:
            image_type = None
        imageid = self._get_image_id(image_type)

        if name is None:
            name = self._generate_instance_name()

        instance_type = self._select_instance_type(resources_needed)

        # startup_script = self._get_startup_script(
        #     resources_needed, queue_name, timeout=timeout)

        startup_script_path = os.path.join(os.getcwd(),
                                           "worker/base_startup_installation.sh")
        with open(startup_script_path) as f:
            startup_script = f.read()

        # self.logger.info(
        #     'Starting EC2 instance of type {}'.format(instance_type))

        kwargs = {
            'BlockDeviceMappings':
                self._get_block_device_mappings(resources_needed),
            'ImageId': imageid,
            'InstanceType': instance_type,
            'MaxCount': 1,
            'MinCount': 1,
            'UserData': startup_script,
            'InstanceInitiatedShutdownBehavior': 'terminate',
            'TagSpecifications': [{
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                    {
                        'Key': 'Team',
                        'Value': 'tools'
                    }]
            }]
        }

        ports = set(ports)

        if any(ports):
            groupid = self._get_security_group(ports)
            kwargs['SecurityGroupIds'] = [groupid]

        if ssh_keypair is not None:
            key_pair_path = ssh_keypair["key_path"]
            kwargs['KeyName'] = ssh_keypair["key_name"]
        else:
            key_name = f"{self.project_id}_key"
            key_pair_path = os.path.join(self.cloud_dsm_base_path, f"{key_name}.pem")
            self.create_key_pair(key_name, key_pair_path)
            kwargs['KeyName'] = key_name

        response = self.compute_client.run_instances(**kwargs)
        instance_id = response['Instances'][0]['InstanceId']
        instance_obj = self.get_instance_from_id(instance_id)

        self.instances.append({
            "name": name,
            "id": instance_id,
            "object": instance_obj
        })
        if blocking:
            while True:
                try:
                    response = self.compute_client.describe_instances(
                        InstanceIds=[instance_id]
                    )
                    instance_data = response['Reservations'][0]['Instances'][0]
                    ip_addr = instance_data.get('PublicIpAddress')
                    if ip_addr:
                        print("ip address: {}".format(ip_addr))
                        break
                except BaseException as e:
                    pass

        # Persist Queue Config and Studio Config
        configs_local_path = os.path.join(self.cloud_dsm_base_path, "configs")
        configs_local_path = os.path.abspath(configs_local_path)
        persist_essential_configs(queue_config, storage_config, configs_local_path)
        configs_instance_path = "configs"

        # Copy the configs Over SCP to the instance
        print(f"Sending config over SCP to {ip_addr}")
        files_sent = False
        while not files_sent:
            try:
                files_sent = scp_send(hostname=ip_addr,
                         username="ubuntu",
                         local_filepath=configs_local_path,
                         instance_filepath=configs_instance_path,
                         key_filepath=key_pair_path)
            except:
                pass

    def _stop_instance(self, instance):
        """
        This function shutsdown the given instance
        :param instance: Instance Object or name
        :returns nothing:
        """
        if isinstance(instance, str):
            instance = self.get_instance_from_id(instance)
        instance.terminate()

    def create_workers(self, queue_config, storage_config, blocking=True,
                       ssh_keypair=None, timeout=300, ports=None):
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
        for _ in range(num_workers):
            self.start_worker(queue_config, storage_config, resources_needed, blocking,
                              ssh_keypair, timeout, ports)

    def shutdown(self):
        """
        This function terminates all EC2 instances
        part of this project.
        :returns nothing:
        """
        for instance in self.instances:
            instance_obj = instance["object"]
            self._stop_instance(instance_obj)

        self.instances = []
