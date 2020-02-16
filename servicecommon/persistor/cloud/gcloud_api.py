from google.cloud import storage
from google.oauth2 import service_account
from framework.interfaces.persistence.persistence import Persistence


class GCloudApi(Persistence):
    '''
    Class acts as means to persist data on the google
    cloud
    '''

    def __init__(self, credentials_dict, bucket_name, file_path, file_name,
                 restore_path=None):
 
        super().__init__()
        self.credentials_dict = credentials_dict
        self.instance = storage.Client.from_service_account_json(
                                            self.credentials_dict)
        self.bucket_name = bucket_name
        self.bucket = self.create_bucket()
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

        return self.instance.create_bucket(self.bucket_name)

    def delete_bucket(self):
        '''
        deletes bucket from google storage
        '''

        self.instance.delete_bucket(self.bucket_name)

    # def set_credentials(self):
    #     '''
    #     Gets credentials from google service json file and retreives
    #     a usable key
    #     '''
    #     return service_account.Credentials.from_service_account_file(
    #        self.credentials_dict,
    #     )

    def persist(self):
        '''
        Pushes file up to google storage
        '''

        self.bucket = self.instance.get_bucket(self.bucket_name)
        blob = self.bucket.blob(self.file_name)
        blob.upload_from_filename(self.file_path)

    def restore(self):
        '''
        Retreives file from google storage
        '''

        self.bucket = self.instance.get_bucket(self.bucket_name)
        blob = self.bucket.blob(self.file_name)
        blob.download_to_filename(self.restore_path)

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_restore_path(self, restore_path):
        self.restore_path = restore_path





