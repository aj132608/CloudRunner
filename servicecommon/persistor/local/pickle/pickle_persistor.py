import pickle

from framework.interfaces.persistence.persistence import Persistence


class PicklePersistor(Persistence):

    def __init__(self, file, base_file_name=".", folder=""):
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
        self.file = file

    def persist(self):
        """
        This function takes in a dictionary and
        persists at the path with the base_file_name
        :param dict: Dictornary to persist
        :returns nothing
        """
        if not self.base_file_name:
            self.base_file_name = "default_pickle"
        if not self.folder[-1] == "/":
            self.folder += "/"
        with open(self.folder + self.base_file_name + '.pkl', 'wb') as fp:
            pickle.dump(self.file, fp)

    def restore(self):
        """
        This function loads a json from the
        base_file_name in the specified folder
        in a dictionary format.
        :params none
        :returns dict: Dictionary created from the
        JSON
        """
        if not self.folder[-1] == "/":
            self.folder += "/"
        file = self.folder + self.base_file_name +'.pkl'
        try:
            pickle_obj = pickle.load(file)
        except Exception as e:
            print(e)

        return pickle_obj
