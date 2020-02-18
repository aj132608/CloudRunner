from google.cloud import storage
from framework.interfaces.persistence.persistence import Persistence


class GCloudStore(Persistence):
    '''
    Class acts as means to persist data on the google
    cloud
    '''

    def __init__(self, credentials_path, bucket_name=None, file_path=None, file_name=None,
                 restore_path=None):
 
        super().__init__()
        self.credentials_dict = credentials_path
        self.instance = storage.Client.from_service_account_json(
                                            self.credentials_dict)
        self.bucket_name = bucket_name
        self.bucket = None
        self.file_path = file_path
        self.file_name = file_name
        if restore_path is None:
            self.restore_path = file_path
        else:
            self.restore_path = restore_path

    def create_bucket(self):
        '''
        creates bucket (db table equivalent) in google storage
        '''
        try:
            bucket = self.instance.get_bucket(self.bucket_name)
        except:
            bucket = None
        if not bucket:
            return self.instance.create_bucket(self.bucket_name)
        else:
            return bucket

    def delete_bucket(self):
        '''
        deletes bucket from google storage
        '''

        self.instance.delete_bucket(self.bucket_name)

    def persist(self):
        '''
        Pushes file up to google storage
        '''

        self.bucket = self.create_bucket()
        self.bucket = self.instance.get_bucket(self.bucket_name)
        blob = self.bucket.blob(self.file_name)

        try:
            blob.upload_from_filename(self.file_path)
        except Exception as e:
            print(e)
            import time
            time.sleep(60)

    def restore(self):
        '''
        Retreives file from google storage
        '''
        self.bucket = self.create_bucket()
        self.bucket = self.instance.get_bucket(self.bucket_name)
        blob = self.bucket.blob(self.file_name)
        blob.download_to_filename(self.restore_path)









