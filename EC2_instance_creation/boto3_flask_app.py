from flask import Flask, request
import boto3
from botocore.client import Config

import pickle
import json
import os
import calendar
import time

from search_space.search_space import SearchSpace
from search_space.populate_search_space import PopulateSearchSpace
from framework.serialize.population.population_serializer import PopulationSerializer
from servicecommon.persistor.local.json.json_persistor import JsonPersistor
from servicecommon.utils.statistics import Statistics
from servicecommon.utils.visualize import Visualize
from servicecommon.utils.evolution_persistor import EvolutionPersistor

# get the values of the following environment variables to provide credentials
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')

# Port 9000 inside the MinIO container
# postgres://db:5432 or {container_image}://{container_name}:{container_port}
ENDPOINT_URL = 'http://172.172.172.1:9000'


# ENDPOINT_URL = "minio/minio://persistenceminio:9000"

def get_boto3_object():
    '''
    retrieves the boto3 object by sending it the proper credentials
    - the endpoint that corresponds to the MinIO container
    - Access and Secret key that were set in using environment variables
    in the MinIO container.
    - the config and region_name arguments are set to a default
    '''

    s3_obj = boto3.resource('s3',
                            endpoint_url=ENDPOINT_URL,
                            aws_access_key_id=MINIO_ACCESS_KEY,
                            aws_secret_access_key=MINIO_SECRET_KEY,
                            config=Config(signature_version='s3v4'),
                            region_name='us-east-1')

    return s3_obj


def get_boto3_client_object():
    '''
    retrieves the boto3 object by sending it the proper credentials
    - the endpoint that corresponds to the MinIO container
    - Access and Secret key that were set in using environment variables
    in the MinIO container.
    - the config and region_name arguments are set to a default
    '''

    s3_obj = boto3.client('s3',
                          endpoint_url=ENDPOINT_URL,
                          aws_access_key_id=MINIO_ACCESS_KEY,
                          aws_secret_access_key=MINIO_SECRET_KEY,
                          config=Config(signature_version='s3v4'),
                          region_name='us-east-1')

    return s3_obj


persistence_server = Flask(__name__)
search_space_obj = SearchSpace()


@persistence_server.route('/')
def index():
    return '''<h1>MineAI Persistence Service</h1>'''


@persistence_server.route('/init', methods=['POST'])
def set_up_search_space():
    global search_space_obj
    pickled_data = request.data
    search_space = pickle.loads(pickled_data)
    search_space_obj = PopulateSearchSpace.populate_search_space(search_space_obj,
                                                                 search_space)
    return '''True'''


@persistence_server.route('/create-test-bucket', methods=['POST'])
def create_test_bucket():
    '''
    This creates the bucket that will contain all the directories
    and files of the experiment.
    expected incoming data format:
    {'directory_name': 'default'} or
    {'directory_name': 'test-run-1-13-2020'}
    returns:
    The name of the bucket that's been created.
    ex: 'test-run-1-13-2020'
    or
    Returns 'Failed', to indicate that no bucket has been created.
    '''

    main_directory_config = request.json

    # get the users specified directory name
    directory_name = main_directory_config['directory_name']

    if directory_name == 'default':
        experiment_id = calendar.timegm(time.gmtime())
        directory_name = f'evolf-test-{experiment_id}'

    s3 = get_boto3_object()

    try:
        # make sure that the directory name is acceptable
        s3.create_bucket(Bucket=directory_name)
    except:
        try:
            # if it already exists, add a 1 at the end
            directory_name += '1'
            s3.create_bucket(Bucket=directory_name)
        except:
            return "Failed"

    return directory_name


@persistence_server.route('/test-file-upload', methods=['POST'])
def test_file_upload():
    '''

    uploads a file to a specific bucket using keys
    Expected incoming data format:
    {
        "file_info": {
            "bucket_name": "test-run-1-13-2020",
            "generation_number": "0",
            "tree_number": "25"
        },
        "persistence_config": {
            "tree_stats": True,
            "tree_visualize": False,
            "tree_graph": True,
            "avg_fitness_graph": False,
            "best_fitness_graph": True
        }
    }
    '''

    # testing code

    # pickled_request_data = request.data
    # file_upload_config = pickle.loads(pickled_request_data)
    # return file_upload_config

    file_upload_config = request.json
    # pickled_request_data = request.data

    # # deserialize the request data
    # file_upload_config = pickle.loads(pickled_request_data)

    # unpack the config
    file_info = file_upload_config['file_info']
    extra_arg_dict = {}
    extra_arg_dict['Metadata'] = file_info
    persistence_config = file_upload_config['persistence_config']

    # unpack persistence config
    tree_stats_selected = persistence_config['tree_stats']
    tree_visualize_selected = persistence_config['tree_visualize']
    tree_graph_selected = persistence_config['tree_graph']
    avg_fitness_graph_selected = persistence_config['avg_fitness_graph']
    best_fitness_graph_selected = persistence_config['best_fitness_graph']

    files_uploaded = []
    s3 = get_boto3_client_object()

    if tree_stats_selected:
        s3.upload_file(
            'requirements.txt', file_info["bucket_name"], 'tree-stats.txt',
            ExtraArgs=extra_arg_dict
        )
        files_uploaded.append("tree-stats.txt")
    if tree_visualize_selected:
        s3.upload_file(
            'requirements.txt', file_info["bucket_name"], 'tree-visualization.txt',
            ExtraArgs=extra_arg_dict
        )
        files_uploaded.append("tree-visualization.txt")
    if tree_graph_selected:
        s3.upload_file(
            'requirements.txt', file_info["bucket_name"], 'tree-graph.txt',
            ExtraArgs=extra_arg_dict
        )
        files_uploaded.append("tree-graph.txt")
    if avg_fitness_graph_selected:
        s3.upload_file(
            'requirements.txt', file_info["bucket_name"], 'avg-fitness-graph.txt',
            ExtraArgs=extra_arg_dict
        )
        files_uploaded.append("avg-fitness-graph.txt")
    if best_fitness_graph_selected:
        s3.upload_file(
            'requirements.txt', file_info["bucket_name"], 'best-fitness-graph.txt',
            ExtraArgs=extra_arg_dict
        )
        files_uploaded.append("best-fitness-graph.txt")

    # add the list of selected and uploaded files to a dictionary so it can be returned
    job_info = {}
    job_info["uploaded_files"] = files_uploaded
    job_info["bucket_name"] = file_info["bucket_name"]

    return job_info


@persistence_server.route('/persist/population', methods=['POST'])
def persist_population():
    data = request.json
    return data


if __name__ == '__main__':
    # runs the flask app.

    # turns on debug mode and sets the host IP address of the
    # app to 0.0.0.0
    persistence_server.run(debug=True, host='0.0.0.0')