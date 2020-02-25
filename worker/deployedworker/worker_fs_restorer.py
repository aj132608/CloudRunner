from fstracker.fs_restorer import FileSystemRestorer
from initilizationservice.initialization_service import InitializationService
from servicecommon.parsers.argumentparsers.fs_restorer_parser import FsRestorerParser

if __name__ == '__main__':

    fs_restorer_arg_parser = FsRestorerParser()

    # Dummy Initializer Path
    initializer_service = InitializationService(fs_restorer_arg_parser.config_path,
                                                fs_restorer_arg_parser.project_id, False, False)

    # Get Storage Object
    storage_object = initializer_service.storage_obj

    # Start Filesystem Restorer
    fs_restorer = FileSystemRestorer(storage_object,
                                     fs_restorer_arg_parser.project_id)
    fs_restorer.restore_environment()