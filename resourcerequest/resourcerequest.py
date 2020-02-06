import GPUtil
import psutil
import platform
import nvidia_smi
from datetime import datetime


class ResourceRequest:
    def __init__(self):
        pass

    def get_resource_usage(self, get_cpu, get_ram, get_gpu=False, available_cores=None):

        if get_cpu:
            # get the current cpu usage
            cpu_usage = psutil.cpu_percent()

            if available_cores is None:
                # get the total number of cores
                available_cores = psutil.cpu_count(logical=False)
            else:
                total_physical_cores = psutil.cpu_count(logical=False)

                if available_cores < total_physical_cores:
                    # the CPU usage is inaccurate
                    pass

    @staticmethod
    def get_adjusted_cpu_usage(available_cores, total_cores, cpu_usage):
        cores_in_use = (cpu_usage / 100) * total_cores

        new_cpu_usage = (cores_in_use / available_cores) * 100

        return new_cpu_usage

    @staticmethod
    def get_num_of_cores_in_use(total_cores, cpu_usage):
        import math

        cores_in_use = (cpu_usage / 100) * total_cores

        return math.ceil(cores_in_use)

