import os
from worker.gcloud_worker import GCloudWorker

instance = GCloudWorker("my-project1-254915-805e652a60d3.json",5,"my-project1-254915",'us-central1-a','bucket',{
    'cpu': 1,
    'ram': 1024,
    'gpu_type':'nvidia-tesla-t4',
    'num_of_gpu':1,
    'disk_type':'pd-ssd',
    'disk_space':10
}, "startup.sh")
instance.create_workers()





