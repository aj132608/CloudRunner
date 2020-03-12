
def export_env_variable(name, value):
    import os
    os.environ[name] = value  # visible in this process + all children

def run_command(command, wait_for_output=True):
    import subprocess
    import shlex
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
    from servicecommon.persistor.local.json.json_persistor import JsonPersistor
    configs_path = persist_path
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

def rand_string(length):
    import random
    import string
    return "".join([random.choice(string.ascii_letters + string.digits)
                    for n in range(length)])

def generate_big_random_bin_file(filename, size):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    :return:void
    """
    import os
    import logging
    with open('%s'%filename, 'wb') as fout:
        fout.write(os.urandom(size))

    logging.log(logging.DEBUG, "Big Random file generated")

def generate_timestamp(base_word=None):
    """

    This function will generate a timestamp id with a given or default base word


    :param base_word: an optional argument if you wanted a specific word for your task. It defaults to 'task'
    :return: task_id: unique string generated for each task submitted
    """
    import calendar
    import time

    # check to see if you should add the default base word
    if base_word is None:
        base_word = "task"

    # generate a number
    id_number = calendar.timegm(time.gmtime())

    # assemble the task id
    timestamp = f"{base_word}_{id_number}"

    return timestamp