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
        "cdsm_compute_access_key": "AKIAWA6NKF4S6U2THRHT",
        "cdsm_compute_secret_key": "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"
    }
}


queue_config = {
    "type": "rmq",
    "endpoint": "amqp://guest:guest@0.tcp.ngrok.io:12474",
    "queue_name": "rabbit_queue_1",
    "exchange_name": "rabbit_exchange_1"
}

storage_config = {
    "type": "s3",
    "region": "us-west-2",
    "env":{
        "cdsm_storage_access_key": "AKIAWA6NKF4SYIQAN6Q4",
        "cdsm_storage_secret_key": "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",
    },
    "endpoint_url": "https://s3-us-west-2.amazonaws.com"
}

# resource = {'cpus':2, 'ram': '2g', 'gpus':0, "num_workers": 1, "image": "ami-d1180894"}
# credential = {
#     "region": "us-west-1",
#     "access_key": "AKIAWA6NKF4S6U2THRHT",
#     "secret_key": "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",
# }
worker = EC2WorkerManager("test_proj2", aws_config)
worker.create_workers(queue_config, storage_config)

