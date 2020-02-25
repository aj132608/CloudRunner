from worker.gcloud_worker import GCloudWorker

instance = GCloudWorker("/Users/mo/Desktop/mineai/CloudRunner/_accesskeys/Cloud Runner-3ddd96d875ef.json", {
    'cpu': 1,
    'ram': 1024,
    'gpu_type':'nvidia-tesla-t4',
    'num_of_gpu': 1,
    'disk_type': 'pd-ssd',
    'disk_space': 10,
    "zone": "us-central1-a",
    "num_workers": 2
}, "test")
instance.create_workers()
# instance.delete_worker('worker-1')
# for inst in instance.get_workers():
#     instance_name = inst["name"]
#     instance.delete_worker(instance)




