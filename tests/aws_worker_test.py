from workermanager.aws_worker import EC2WorkerManager

aws_config = {
    "resources": {
        "cpus": 2,
        "ram": '2g',
        "gpus": 0,
        "num_workers": 1,
        "hdd": '60g'
    },
    "region": "us-west-1",
    "env": {
        "cdsm_compute_access_key": "AWS_COMPUTE_ACCESS_KEY_ID",
        "cdsm_compute_secret_key": "AWS_COMPUTE_SECRET_KEY_ID"
    }
}

queue_config = {
    "type": "rmq"
}

storage_config = {
    "type": "aws"
}

# resource = {'cpus':2, 'ram': '2g', 'gpus':0, "num_workers": 1, "image": "ami-d1180894"}
# credential = {
#     "region": "us-west-1",
#     "access_key": "AKIAWA6NKF4S6U2THRHT",
#     "secret_key": "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",
# }
worker = EC2WorkerManager("test_proj2", aws_config)
worker.create_workers(queue_config, storage_config)

