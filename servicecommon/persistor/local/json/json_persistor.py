import json
import os

from framework.interfaces.persistence.persistence import Persistence


class JsonPersistor(Persistence):

    def __init__(self, dict, base_file_name="file", folder="."):
        """
        This constructor initializes the name of the file to
        persist at what path.

        :param base_file_name: Name of the file without the .json
        extension
        :param folder: Location of the file to persist
        :returns nothing
        """
        super().__init__()
        self.base_file_name = base_file_name
        self.folder = folder
        self.dict = dict

    def persist(self):
        """
        This function takes in a dictionary and
        persists at the path with the base_file_name
        :param dict: Dictionary to persist
        :returns nothing
        """
        if not self.base_file_name:
            self.base_file_name = "default_dict"
        if len(self.folder.strip()):
            if not self.folder[-1] == "/":
                self.folder += "/"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        with open(self.folder + self.base_file_name + '.json', 'w') as fp:
            json.dump(self.dict, fp, indent=4)

    def restore(self):
        """
        This function loads a json from the
        base_file_name in the specified folder
        in a dictionary format.
        :params none
        :returns dict: Dictionary created from the
        JSON
        """
        if len(self.folder.strip()):
            if not self.folder[-1] == "/":
                self.folder += "/"
        file = self.folder + self.base_file_name + '.json'

        with open(file) as json_file:
            dict = json.load(json_file)

        return dict
