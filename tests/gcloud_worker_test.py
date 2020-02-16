from worker.gcloud_worker import GCloudWorker

instance = GCloudWorker("storage/my-project1-254915-24b914b345ec.json",2,"my-project1-254915",'us-central1-a','bucket',{
    'cpu': 2,
    'ram': 2048,
    'gpu_type':'nvidia-tesla-t4',
    'num_of_gpu':1,
    'disk_type':'pd-ssd',
    'disk_space':10
})
instance.create_workers()


