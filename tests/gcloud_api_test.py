from servicecommon.persistor.cloud.gcloud.gcloud_store import GCloudStore

api = GCloudStore('my-project1-254915-805e652a60d3.json','new_bucket', 'tests/funny.PNG', 'funny',
                 'queue_tests')
api.persist()    