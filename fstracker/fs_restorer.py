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

    def __init__(self, storage_communicator, project_name, job_id, filesystem_config=None):
        """
        This function sets up the
        :param storage_communicator: Storage Communication Object
        :param filesystem_config: Filesystem config
        """
        self.storage_communicator = storage_communicator
        self.storage_communicator.set_bucket_name(project_name)

        self.filesystem_config = filesystem_config
        self.job_id = job_id

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
        filesystem_tar_base_name = "filesystem"
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
                                     extract_path=f"{os.getcwd()}/{self.job_id}")
        tar_persistor.restore()

    def restore_environment(self):
        """

        :return:
        """
        self.download_filesystem()
        self.extract_tar(self.job_id, os.getcwd())

        curr_dir = os.getcwd()

        os.chdir(f"{curr_dir}/{self.job_id}")
        assert "setup.sh" in os.listdir(os.getcwd())
        os.system("bash setup.sh")

        with open("source_venv.sh", 'w') as rsh:
            rsh.write(f"source cloud_venv/bin/activate")

        os.chdir(curr_dir)


if __name__ == "__main__":
    # #### AWS/MINIO Test ####
    # credentials_dict = {
    #     'endpoint_url': 'http://127.0.0.1:9000',
    #     'access_key': 'minioadmin',
    #     'secret_key': 'minioadmin',
    #     'region': None
    # }
    #
    # storage_obj = S3Store(credentials_dict)
    # fsr = FileSystemRestorer(storage_obj, project_name="test-project-mineai")
    # fsr.restore_environment()

    ### GCloud Store Test ####
    credentials_path = 'my-project1-254915-805e652a60d3.json'
    storage_obj = GCloudStore(credentials_path=credentials_path)

    fsr = FileSystemRestorer(storage_obj, project_name="test-project-mineai", job_id="test_job")
    fsr.restore_environment()
