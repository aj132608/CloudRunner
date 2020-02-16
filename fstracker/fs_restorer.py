import os

from servicecommon.persistor.local.tar.tar_persistor import TarPersistor


class FileSystemRestorer:
    """
    This function restores the file system and the environment.
    """

    def __init__(self, storage_communicator, filesystem_config=None):
        """
        This function sets up the
        :param storage_communicator: Storage Communication Object
        :param filesystem_config: Filesystem config
        """
        self.storage_communicator = storage_communicator
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
        filesystem_tar_name = "filesystem.tar"
        path_to_restore = os.path.join(os.getcwd(), "filesystem")
        self.storage_communicator.restore("filesystem", filesystem_tar_name,
                                        path_to_restore)
        return path_to_restore, \
               filesystem_tar_name

    def extract_tar(self, tar_path, tar_name):
        """
        This function extracts the tar file.
        :param tarred_file_path: File path to the tar
        :return:
        """

        tar_persistor = TarPersistor(base_file_name=tar_name,
                                     folder=tar_path,
                                     paths_to_tar=None,
                                     extract_path=True)
        tar_persistor.restore()

    def restore_environment(self):
        """

        :return:
        """
        path_to_restore, filesystem_tar_name = self.download_filesystem()
        self.extract_tar(path_to_restore, filesystem_tar_name)

        curr_dir = os.getcwd()

        os.chdir(f"{path_to_restore}/filesystem")
        assert "setup.sh" in os.listdir()
        os.system("source setup.sh")

        with open("source_venv.sh", 'w') as rsh:
            rsh.write(f"source cloud_venv/bin/activate")

        os.chdir(curr_dir)




