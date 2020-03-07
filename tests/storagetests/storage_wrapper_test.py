from completionservice.storage_wrapper import StorageWrapper
import os

if __name__ == "__main__":
    storage_config = {
        "type": "minio",
        "endpoint_url": "http://localhost:9000",
        "region": "",
        "env": {
            "cdsm_storage_access_key": "minioadmin",
            "cdsm_storage_secret_key": "minioadmin"
        }
    }

    print(storage_config)

    storage_wrapper = StorageWrapper(storage_config=storage_config)

    storage_wrapper.get_job_data(username='cloudrunneralex',
                                 project_id='project0',
                                 experiment_id='experiment0',
                                 job_id='job0',
                                 local_path='job.tar')
