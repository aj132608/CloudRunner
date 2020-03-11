import os
import random
import shlex
import string

import subprocess

import yaml

from servicecommon.persistor.local.json.json_persistor import JsonPersistor

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


def rand_string(length):
    return "".join([random.choice(string.ascii_letters + string.digits)
                    for n in range(length)])


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


def run_command(command, wait_for_output=True):
    process = subprocess.Popen(shlex.split(command),
                               stdout=subprocess.PIPE)

    if wait_for_output:
        complete_output = ""
        while True:
            output = process.stdout.readline()
            complete_output += output.decode("utf-8")
            if output == b'' and process.poll() is not None:
                break
            # if output:
                # print(output.strip())
        rc = process.poll()
    else:
        rc, complete_output = None, None
    return rc, complete_output, process


def persist_essential_configs(queue, storage, persist_path):
    """
    Persists the queue_config and the storage_config for the
    worker as a JSON
    :return:
    """
    configs_path = persist_path
    # if not os.path.exists(configs_path):
    #     os.makedirs(configs_path)

    queue_config = queue["config"]
    queue_file_name = queue["filename"]

    storage_config = storage["config"]
    storage_file_name = storage["filename"]

    json_persistor = JsonPersistor(queue_config,
                                   queue_file_name,
                                   configs_path)
    json_persistor.persist()

    json_persistor = JsonPersistor(storage_config,
                                   storage_file_name,
                                   configs_path)
    json_persistor.persist()


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
