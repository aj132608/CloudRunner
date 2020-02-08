from google.cloud import storage

def main():

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()
    bucket_name = "tubuck"

    # Creates the new bucket
    bucket = storage_client.create_bucket(bucket_name)
    print(f"Bucket {bucket.name} created.\n")

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)

if __name__ == "__main__":
    main()