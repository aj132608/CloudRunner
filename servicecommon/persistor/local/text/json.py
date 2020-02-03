import json
import os

from framework.interfaces.persistence.persistence import Persistence


class TextJsonPersistor(Persistence):

    def __init__(self, object=None, folder=".", filename="textfile"):
        super().__init__()
        self.object = object
        self.folder = folder
        self.filename = filename

        self.extension = "txt"

        self.full_filepath = os.path.join(self.folder, f"{self.filename}.{self.extension}")

    def persist(self):
        assert isinstance(self.object, dict) or isinstance(self.object, list), "Expected a Dictionary"
        with open(self.full_filepath, 'w') as file:
            json.dump(self.object, file, indent=4)

        return True

    def restore(self):
        if not os.path.exists(self.full_filepath):
            raise FileNotFoundError

        with open(self.full_filepath, 'r') as file:
            file_contents = file.read()
            dictionary = json.loads(file_contents)

        return dictionary
