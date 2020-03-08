from storage.storage_creator import StorageCreator

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

    creator_obj = StorageCreator(storage_config=storage_config)
    storage_obj = creator_obj.build_storage_object()

    # response = storage_obj.create_bucket('testbucket', start_new=True)
    # print(response)

    storage_obj.persist_file(s3_key='alex.jirovsky/project0/experiment0/completion/job0.tar',
                             local_file_path='requirements.txt',
                             bucket='cloudrunneralex')
