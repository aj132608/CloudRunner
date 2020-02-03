from servicecommon.persistor.local.tar.tar_persistor import TarPersistor

list_of_paths = ["./__init__.py", "./setup", "./readme.md"]
extraction_path = "."

# self, base_file_name="file", folder=".", paths_to_tar=[], extract_path=None
tar_persist_obj = TarPersistor("test_tar", paths_to_tar=list_of_paths, extract_path=extraction_path)

tar_persist_obj.persist()

extraction_folder_path = tar_persist_obj.restore()

print(f"Extracted files are located here: {extraction_folder_path}")
