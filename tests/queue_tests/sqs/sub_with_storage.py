from completionservice.completion_service import CompletionService, QueueMaster, StorageCreator


if __name__ == "__main__":
    queue_config = {
        "type": "sqs",
        "env": {
            "cdsm_queue_access_key": "AKIAXV2ATPWYVZGBHUCT",
            "cdsm_queue_secret_key": "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"
        },
        "region": "us-west-2",
        "queue_name": "practicequeue.fifo"
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

    storage_obj = StorageCreator(storage_config=storage_config).build_storage_object()

    master_obj = QueueMaster(queue_config=queue_config,
                             storage_obj=storage_obj)

    publisher = master_obj.build_publisher_object()

    response = publisher.get_client_object().get_queue_url(
        QueueName='myqueue.fifo'
    )

    queue_url = response['QueueUrl']

    queue_config['queue_url'] = queue_url

    completion_obj = CompletionService(queue_config=queue_config,
                                       storage_config=storage_config)