from multiprocessing import Process
from flask import Flask, request, render_template


class MultiprocessingService:
    def __init__(self):
        self.num_of_cores = ""
        self.system = ""
        self.cpu_usage = ""
        self.available_ram = ""
        self.total_ram = ""


multiprocessing_service = Flask(__name__)
multiprocessing_obj = MultiprocessingService()


@multiprocessing_service.route('/', methods=['GET'])
def index():
    return "Multiprocessing Service"


@multiprocessing_service.route('/get-system-info', methods=['GET'])
def get_system_info():
    global multiprocessing_obj
    return render_template('system_info.html', num_of_cores=multiprocessing_obj.num_of_cores,
                           system=multiprocessing_obj.system, cpu_usage=multiprocessing_obj.cpu_usage,
                           available_ram=multiprocessing_obj.available_ram, total_ram=multiprocessing_obj.total_ram)


@multiprocessing_service.route('/system-info', methods=['POST'])
def set_system_info():
    """

    This route can receive only post requests and populates the system info
    class variables from the MultiprocessingService class.

    sample input:

    {
        "num_of_cores": "6",
        "system": "Windows",
        "cpu_usage": "33",
        "available_ram": "5GB",
        "total_ram": "16GB"
    }

    :return:
    """

    global multiprocessing_obj
    # get the request data
    data = request.json

    # unpack the dictionary into the respective class variables
    multiprocessing_obj.num_of_cores = data['num_of_cores']
    multiprocessing_obj.system = data['system']
    multiprocessing_obj.cpu_usage = data['cpu_usage']
    multiprocessing_obj.available_ram = data['available_ram']
    multiprocessing_obj.total_ram = data['total_ram']

    return "System Info Updated"


if __name__ == "__main__":
    multiprocessing_service.run(port=8080, debug=True, use_reloader=True)
