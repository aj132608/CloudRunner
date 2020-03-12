from servicecommon.interfaces.persistence.persistor import Persistor
from servicecommon.interfaces.persistence.restorer import Restorer


class Persistence(Persistor, Restorer):

    def persist(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_restore_path(self, restore_path):
        self.restore_path = restore_path

    def set_bucket_name(self, bucket_name):
        self.bucket_name = bucket_name
