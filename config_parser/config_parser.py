import json

with open(config.json) as config_file:
    data = json.load(config_file)

local_cpu = data["Local"]["CPU"]
local_gpu = data["Local"]["GPU"]
local_ram = data["Local"]["RAM"]
local_queue_type = data["Local"]["queue_type"]

aws_cpu = data["AWS"]["CPU"]
aws_gpu = data["AWS"]["GPU"]
aws_ram = data["AWS"]["RAM"]
aws_queue_type = data["AWS"]["queue_type"]
aws_num_workers = data["AWS"]["Number_of_workers"]
aws_credentials = data["AWS"]["Credentials"]
aws_endpoints = data["AWS"]["Endpoints"]

gcloud_cpu = data["GCloud"]["CPU"]
gcloud_gpu = data["GCloud"]["GPU"]
gcloud_ram = data["GCloud"]["RAM"]
gcloud_num_workers = data["GCloud"]["Number_of_workers"]
gcloud_credentials = data["GCloud"]["Credentials"]
gcloud_endpoints = data["GCloud"]["Endpoints"]