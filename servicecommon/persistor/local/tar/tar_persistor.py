import tarfile
import os
from tqdm import trange

from framework.interfaces.persistence.persistence import Persistence


class TarPersistor(Persistence):

    def __init__(self, base_file_name="file", folder=".", paths_to_tar=None, extract_path=None):
        """
        This constructor initializes the name of the file to
        persist at what path.
        :param base_file_name: Name of the tar file
        :param folder: Location of the file to persist
        :returns nothing
        """
        super().__init__()
        if paths_to_tar is None:
            paths_to_tar = []
        self.base_file_name = base_file_name
        self.folder = folder
        self.paths_to_tar = paths_to_tar
        self.extract_path = extract_path

    def persist(self):
        """
        This function takes in a list of paths and
        adds the file at each path to a tar file with
        a specified path and file name.
        :returns nothing
        """

        # if a file name wasn't assigned, give it a default name
        if not self.base_file_name:
            self.base_file_name = "default_tar"

        # make sure that there is a "/" at the end of the path
        if len(self.folder.strip()):
            if not self.folder[-1] == "/":
                self.folder += "/"

        # if the path doesn't exist, create it
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        # Add the temporary json file to a .tar file
        tar_path = f'{self.folder + self.base_file_name}.tar'
        with tarfile.open(tar_path, 'w') as tar_handle:
            # add each path to the tarfile
            for path_num in trange(len(self.paths_to_tar)):
                path = self.paths_to_tar[path_num]
                tar_handle.add(path)

        return tar_path

    def restore(self):
        """
        This function extracts the files and
        directories from a specific tar file to a
        folder at a specified path.
        :params none
        :returns path to folder containing extracted
        files and directories.
        """

        # make sure that the folder has a "/" at the end
        if len(self.folder.strip()):
            if not self.folder[-1] == "/":
                self.folder += "/"

        # if the extract path isn't assigned, assign
        # it to the location of the tar file in a
        # folder named extracted_tar_files
        if self.extract_path is None:
            self.extract_path += self.folder
        # make sure that the extraction path has a
        # "/" at the end
        else:
            if len(self.extract_path.strip()):
                if not self.extract_path[-1] == "/":
                    self.extract_path += "/"

            # self.extract_path += "extracted_tar_files/"

        # if the path doesn't exist, create it
        if not os.path.exists(self.extract_path):
            os.makedirs(self.extract_path)

        file = self.folder + self.base_file_name + '.tar'

        # open and extract the tarfile contents to
        # extract_path
        tar = tarfile.open(file)
        tar.extractall(path=self.extract_path)
        tar.close()

        return self.extract_path