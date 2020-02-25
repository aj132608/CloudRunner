import argparse
import os


class FsRestorerParser:
    """
    This class adds the command line argument
    supplier to the File System Restorer
    """

    def __init__(self):
        self.config_path, self.project_id = self.add_parser()

    def add_parser(self):
        """""
        This function takes the config path and returns the config
        as a dictionary
        :return config: A dictionary parsed from the supplied config path
        """""
        parser = argparse.ArgumentParser(description="This server is to initialize Cloud Runner. \n"
                                                     "This server must be started from the root of the directory"
                                                     "where the project is setup")
        parser.add_argument("--config",
                            help="The Json file without the extension")
        parser.add_argument("--project_id",
                            help="Project ID")

        args = parser.parse_args()
        # Read the Config File
        config_path = args.config
        project_id = args.project_id

        return config_path, project_id
