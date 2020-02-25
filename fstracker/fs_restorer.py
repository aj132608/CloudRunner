import os

# from fstracker.fs_tracker import FileSystemTracker
from fstracker.fs_tracker import FileSystemTracker
from servicecommon.persistor.cloud.aws.s3_store import S3Store
from servicecommon.persistor.cloud.gcloud.gcloud_store import GCloudStore
from servicecommon.persistor.local.tar.tar_persistor import TarPersistor


class FileSystemRestorer:
    """
    This function restores the file system and the environment.
    """

    def __init__(self, storage_communicator, project_name, filesystem_config=None):
        """
        This function sets up the
        :param storage_communicator: Storage Communication Object
        :param filesystem_config: Filesystem config
        """
        self.project_name = project_name
        self.storage_communicator = storage_communicator
        self.storage_communicator.set_bucket_name(project_name)

        self.filesystem_config = filesystem_config

        if self.filesystem_config is not None:
            client_config = self.filesystem_config.get("client_config", None)
            if client_config is not None:
                self.project_folder_name = client_config.get("project_folder_name")
                self.python_script = client_config.get("python_script")

    def download_filesystem(self):
        """
        This function uses the storage_communicator object
        to download the filesystem tar
        :return:
        """
        filesystem_tar_base_name = f"{self.project_name}_fs"
        filesystem_tar_name = f"{filesystem_tar_base_name}.tar"
        path_to_restore = os.path.join(os.getcwd(), filesystem_tar_name)

        self.storage_communicator.set_restore_path(path_to_restore)
        self.storage_communicator.set_file_name(filesystem_tar_name)
        self.storage_communicator.restore()

    def extract_tar(self, tar_name, tar_path):
        """
        This function extracts the tar file.
        :param tarred_file_path: File path to the tar
        :return:
        """

        tar_persistor = TarPersistor(base_file_name=tar_name,
                                     folder=tar_path,
                                     paths_to_tar=None,
                                     extract_path=f"{os.getcwd()}/{self.project_name}_fs")
        tar_persistor.restore()

    def restore_environment(self):
        """

        :return:
        """
        self.download_filesystem()
        self.extract_tar(f"{self.project_name}_fs", os.getcwd())

        curr_dir = os.getcwd()

        os.chdir(f"{curr_dir}/{self.project_name}_fs")
        assert "setup.sh" in os.listdir(os.getcwd())
        os.system("bash setup.sh")

        with open("source_venv.sh", 'w') as rsh:
            rsh.write(f"source cloud_venv/bin/activate")

        os.chdir(curr_dir)
