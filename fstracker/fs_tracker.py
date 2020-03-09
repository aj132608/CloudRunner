import os
import sys
import logging

from servicecommon.persistor.local.tar.tar_persistor import TarPersistor


class FileSystemTracker:
    """
    This class is part of the initialization routine for cloud runner
    and tracks the environment and the file system.

    Note: The whole project needs to be running in a virtual env.
    """

    def __init__(self, path, temp_project_path, storage_communicator, project_name,
                 project_id, config, config_path,
                 container=None, args=None):
        """
        The constructor initializes the class variables
        :param path: Path to the python script or
        the folder containing the project
        :param temp_project_path: Project name to attach to this
        file system
        """
        self.project_id = project_id
        self.config = config

        # Get the Project path
        original_project_path, python_script_name = self.construct_project_path(path)

        # Get the project folder name
        project_folder_name = os.path.basename(original_project_path)

        # Create the temporary folder
        self.temp_project_path = os.path.abspath(temp_project_path)
        if not os.path.exists(self.temp_project_path):
            os.makedirs(self.temp_project_path)

        # Copy the project files to the temporary folder
        project_tar_path = os.path.join(self.temp_project_path, project_folder_name)
        self._copy_files(original_project_path, project_tar_path)
        # Copy config file
        if config_path.find(".josn") == -1:
            config_path = f"{config_path}.json"
        self._copy_files(config_path, temp_project_path)

        # Create Scripts for Python
        self.create_python_installation_script()
        self.create_venv_init_script()

        # Create the pip requirements file
        os.system(f"pip freeze > {self.temp_project_path}/requirements.txt")

        # Create VAR Script export
        self.create_env_var_export_script()

        # Create setup script
        self.create_setup_script("cloud_venv/bin/activate")

        # Setup script
        self.storage_communicator = storage_communicator
        self.storage_communicator.set_bucket_name(project_name)

        # Get the Environment
        self.env = dict(os.environ)
        self.env["client_config"] = {
            "project_folder_name": project_folder_name
        }

    def extract_python_version_minor(self):
        """

        :return:
        """
        python_version_info = sys.version_info
        python_version = f"{python_version_info.major}.{python_version_info.minor}"
        return python_version

    def extract_python_version_major(self):
        """

        :return:
        """
        python_version_info = sys.version_info
        python_version = f"{python_version_info.major}"
        return python_version

    def create_python_installation_script(self):
        """

        :return:
        """
        file_path = os.path.join(self.temp_project_path, "python_installer.sh")
        python_version = self.extract_python_version_minor()
        with open(file_path, 'w') as rsh:
            rsh.write(f"add-apt-repository -y ppa:deadsnakes/ppa\n"
                      f"apt-get update\napt-get install -y python{python_version}")

    def create_venv_init_script(self):
        """

        :return:
        """
        file_path = os.path.join(self.temp_project_path, "venv_creator.sh")
        python_version_minor = self.extract_python_version_minor()
        python_version_major = self.extract_python_version_major()
        with open(file_path, 'w') as rsh:
            rsh.write(f"apt-get install -y python{python_version_minor}-venv\napt-get install -y python"
                      f"{python_version_major}-venv\npython{python_version_minor} -m venv cloud_venv")

    def _copy_files(self, src, dst):
        """

        :param project_path:
        :param venv_path:
        :return:
        """
        from distutils.dir_util import copy_tree
        try:
            copy_tree(src, dst)
        except:
            import shutil
            file_name = os.path.basename(src)
            shutil.copyfile(src, f"{dst}/{file_name}")

    def construct_project_path(self, path):
        """
        This function checks if the path provided
        refers to a python path or not.
        :param path: Path
        :returns project_path:
        """
        project_path = os.path.abspath(os.path.dirname(path))

        if path.find(".py") != -1:
            python_script = os.path.abspath(os.path.basename(path))
        else:
            python_script = None

        if not project_path == os.getcwd():
            project_path = os.getcwd()

        return project_path, python_script

    def tar_job(self):
        """
        This function tars the directories of the path
        and stores them in a temporary location.
        :returns tar_file_path: The tarred up version
        of the project.
        """
        curr_dir = os.getcwd()

        os.chdir(self.temp_project_path)
        logging.log(level=logging.INFO, msg="Tarring up Filesystem and Environment")
        tar_name = f"{self.project_id}_fs"
        tar_persistor = TarPersistor(base_file_name=tar_name,
                                     folder=".",
                                     paths_to_tar=os.listdir(),
                                     extract_path=False)
        _ = tar_persistor.persist()

        os.chdir(curr_dir)

        tar_path = os.path.join(self.temp_project_path, tar_name) + ".tar"
        return tar_path

    def create_setup_script(self, venv_command_path):
        """

        :return:
        """
        setup_script_path = os.path.join(self.temp_project_path, "setup.sh")
        with open(setup_script_path, 'w') as rsh:
            rsh.write(f"bash python_installer.sh\n"
                      f"bash venv_creator.sh\n"
                      f"source {venv_command_path}\n"
                      f"pip install -r requirements.txt\n"
                      f"source {venv_command_path}"
                      f"bash export_vars.sh")

    def _cleanup(self):
        """

        :return:
        """
        import shutil
        shutil.rmtree(self.temp_project_path)

    def create_env_var_export_script(self):
        env_vars = self.create_user_env_var_dict()
        var_command = ""

        for var_name in env_vars:
            var_command += f"export {var_name}={env_vars[var_name]}\n"

        env_vars_script_path = os.path.join(self.temp_project_path,
                                            "export_vars.sh")
        with open(env_vars_script_path, 'w') as rsh:
            rsh.write(var_command)

    def create_user_env_var_dict(self):
        """

        :return:
        """
        env_vars = {}
        computes = self.config.get("compute")
        for compute in computes:
            compute_dict = computes[compute]
            env = compute_dict.get("env", None)
            if env is not None:
                for env_var in env:
                    env_var_name_in_sys = env[env_var]
                    env_vars[env_var_name_in_sys] = os.environ.get(env_var_name_in_sys)

        storage_vars = self.config.get("storage").get("env", None)
        if storage_vars is not None:
            for var in storage_vars:
                env_var_name_in_sys = storage_vars[var]
                env_vars[env_var_name_in_sys] = os.environ.get(env_var_name_in_sys)

        queue_vars = self.config.get("queuingservices").get("env", None)
        if queue_vars is not None:
            for var in queue_vars:
                env_var_name_in_sys = queue_vars[var]
                env_vars[env_var_name_in_sys] = os.environ.get(env_var_name_in_sys)

        return env_vars

    def persist(self):
        """
        This function persists the filesystem onto a storage
        subject provided as an object in the constructor.
        :return:
        """
        tarred_fs = self.tar_job()
        self.storage_communicator.set_file_name(f"{self.project_id}_fs.tar")
        self.storage_communicator.set_file_path(tarred_fs)
        self.storage_communicator.persist()
        self._cleanup()


#### AWS/MINIO Test ####
# credentials_dict = {
#     'endpoint_url': 'http://127.0.0.1:9000',
#     'access_key': 'minioadmin',
#     'secret_key': 'minioadmin',
#     'region': None
# }
# storage_obj = S3Store(credentials_dict)
#
# fst = FileSystemTracker(os.getcwd(), "../../temp/test_proj/", storage_obj, project_name="test-project-mineai")
# fst.persist_filesystem()


#### GCloud Store Test ####
# credentials_path = 'my-project1-254915-805e652a60d3.json'
# storage_obj = GCloudStore(credentials_path=credentials_path)
#
# fst = FileSystemTracker(os.getcwd(), "../../temp/test_proj/", storage_obj,
#                         project_name="test-project-mineai", job_id="test_job")
# fst.persist_filesystem()