import os
import yaml
from servicecommon.ssh_utils import ssh_exec_cmd

_aws_instance_specs = {
    'c4.large': {
        'cpus': 2,
        'ram': '3.75g',
        'gpus': 0
    },
    'c4.xlarge': {
        'cpus': 4,
        'ram': '7.5g',
        'gpus': 0
    },
    'c4.2xlarge': {
        'cpus': 8,
        'ram': '15g',
        'gpus': 0
    },
    'c4.4xlarge': {
        'cpus': 16,
        'ram': '30g',
        'gpus': 0
    },
    'p2.xlarge': {
        'cpus': 4,
        'ram': '61g',
        'gpus': 1
    },
    'c4.8xlarge': {
        'cpus': 36,
        'ram': '60g',
        'gpus': 0
    },
    'p2.8xlarge': {
        'cpus': 32,
        'ram': '488g',
        'gpus': 8
    },
    'p2.16xlarge': {
        'cpus': 64,
        'ram': '732g',
        'gpus': 16
    }
}


def initialize_worker_type_in_cluster(type, experiment_dir, ip_addr, key_pair_path, logger,
                                      master_token_filepath):

    logger.info("Waiting for Docker to be installed")
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
        logger.info("Initializing Master .... ")
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
                logger.info("Master Setup complete..")
                break
            except Exception as e:
                logger.warning(e)
                continue

        with open(os.path.join(experiment_dir, master_token_filepath), 'w') as f:
            f.write(token)

    elif type == "worker":
        logger.info("Connecting Worker to Master .... ")
        with open(os.path.join(experiment_dir, master_token_filepath), 'r') as f:
            command = f.read()

        command = f"sudo {command}"
        worker_initialized = False
        while not worker_initialized:
            _, ssh_stdout, ssh_stderr = ssh_exec_cmd(hostname=ip_addr,
                                                     username="ubuntu",
                                                     key_filepath=key_pair_path, command=command)

            swarm_join_response = ssh_stdout.read().splitlines()
            swarm_join_error = ssh_stderr.read().splitlines()

            if swarm_join_error:
                if swarm_join_error[0].decode().find("node is already part of a swarm") != -1:
                    worker_initialized = True

            if (len(swarm_join_response) > 1 and
                    not len(swarm_join_error)):
                worker_initialized = True

            logger.debug(f"Swarm Join Out: {swarm_join_response}")
            logger.debug(f"Swarm Join Error: {swarm_join_error}")


def insert_script_into_startup_script(script_to_insert, startup_script_str):
    """

    :param script_to_insert:
    :param startup_script_str:
    :return:
    """
    if script_to_insert is None:
        return startup_script_str

    try:
        with open(os.path.abspath(os.path.expanduser(
                script_to_insert))) as f:
            user_startup_script_lines = f.read()

        # user_startup_script_lines.rstrip()
        user_startup_script_lines = user_startup_script_lines.splitlines()


    except BaseException:
        if script_to_insert is not None:
            print("User startup script (%s) cannot be loaded" %
                  script_to_insert)
        return startup_script_str

    startup_script_lines = startup_script_str.splitlines()
    new_startup_script_lines = []
    for line in startup_script_lines:
        new_startup_script_lines.append("%s\n" % line)

    for line in user_startup_script_lines:
        new_startup_script_lines.append("%s\n" % line)

    new_startup_script = "".join(new_startup_script_lines)
    # print('Inserting the following user startup script'
    #       ' into the default startup script:')
    # print("\n".join(startup_script_lines))

    return new_startup_script

def _get_aws_ondemand_prices(instances=_aws_instance_specs.keys()):
    """
    This function returns the ondemand pricing as a dictionary.
    The prices are read externally from a prices yaml file.
    :param instances: Dictionary describing the type of instances
    :returns: Dictionary containing the prices for each instance.
    """
    # TODO un-hardcode the us-east as a region
    # so that prices are being read for a correct region

    price_path = os.path.join(
        os.path.dirname(__file__),
        f'{os.getcwd()}/workermanager/aws_prices.yaml')
    with open(price_path, 'r') as f:
        data = yaml.load(f.read())

    return {i: data[i] for i in instances}


def memstr_to_int(string):
    """
    This function converts a memory string
    into its integer equivalent. Essentialy used by the
    worker to set up resources.

    :param string: String containing the memory
    :returns:
    """
    if not isinstance(string, str):
        string = str(string)
    conversion_factors = [
        ('Mb', 2 ** 20), ('MiB', 2 ** 20), ('m', 2 ** 20), ('mb', 2 ** 20),
        ('Gb', 2 ** 30), ('GiB', 2 ** 30), ('g', 2 ** 30), ('gb', 2 ** 30),
        ('kb', 2 ** 10), ('k', 2 ** 10)
    ]
    for k, f in conversion_factors:
        if string.endswith(k):
            return int(float(string.replace(k, '')) * f)
    return int(string)
