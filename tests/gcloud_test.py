from storage.gcloud_api import GCloudApi


app = GCloudApi("storage/my-project1-254915-24b914b345ec.json")

# app.create_bucket("new_bucket")
app.restore("my-project1-254915.appspot.com", "tests/funny.PNG")