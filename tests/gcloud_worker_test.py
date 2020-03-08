from workermanager.gcloud_worker import GCloudWorkerManager

worker_config = {
    "env": {
        "cdsm_compute_cred_path": "/Users/mo/Desktop/mineai/Cloud Runner Extras/_accesskeys/MineAI-5d1871963a9d.json",
    },
    "resources": {
        'cpus': 1,
        # 'ram': 1024,
        'gpu_type': 'nvidia-tesla-t4',
        'gpus': 0,
        'hdd': '10g',
        "num_workers": 1
    },

    "zone": "us-central1-a"
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

gcwm = GCloudWorkerManager("test-proj2", worker_config)
gcwm.create_workers(queue_config, storage_config, ports=[9000, 12474])


# from servicecommon.scp import scp_send
#
# ip = "34.68.78.237"
# username = "mohak_kant1amg"
# scp_send(ip, username, "/Users/mo/Desktop/mineai/CloudRunner/setup.sh",
#          "/setup.sh", "/.ssh/gcloud_test.pub")