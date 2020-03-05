import os
import shlex
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

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    complete_output = ""
    while True:
        output = process.stdout.readline()
        complete_output += output.decode("utf-8")
        if output == b'' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc, complete_output

def persist_essential_configs(queue_config, storage_config, persist_path):
    """
    Persists the queue_config and the storage_config for the
    worker as a JSON
    :return:
    """
    configs_path = persist_path
    if not os.path.exists(configs_path):
        os.makedirs(configs_path)

    json_persistor = JsonPersistor(queue_config,
                                   "queue_config",
                                   configs_path)
    json_persistor.persist()

    json_persistor = JsonPersistor(storage_config,
                                   "storage_config",
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