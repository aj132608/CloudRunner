from completionservice.completion_service import CompletionService


if __name__ == "__main__":
    queue_config = {
        "type": "rmq",
        "endpoint": "amqp://guest:guest@localhost",
        "queue_name": "project_queue",
        "exchange_name": "project_exchange"
    }

    storage_config = {
        "type": "minio",
        "endpoint_url": "http://localhost:9000",
        "region": "",
        "env": {
            "cdsm_storage_access_key": "minioadmin",
            "cdsm_storage_secret_key": "minioadmin"
        }
    }

    completion_obj = CompletionService(queue_config=queue_config,
                                       storage_config=storage_config)
