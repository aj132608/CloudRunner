from storage.gcloud_api import GCloudApi


app = GCloudApi("storage/my-project1-254915-24b914b345ec.json", "new_bucket",
                "tests/funny.PNG", "funny")
app.persist()