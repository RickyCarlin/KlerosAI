import os
import json

class FileUtils:

    @staticmethod
    def path_exists(path):
        return os.path.exists(path)

    @staticmethod
    def path_directory(path):
        return os.path.isdir(path)

    @staticmethod
    def path_file(path):
        return os.path.isfile(path)

    @staticmethod
    def current_directory():
        return os.getcwd()

    @staticmethod
    def create_directory(path):
        os.makedirs(path)
        return

    @staticmethod
    def create_directory_if_not_exists(path):
        if not FileUtils.path_exists(path):
            FileUtils.create_directory(path)
        return
    
    @staticmethod
    def join_paths(path1, path2):
        return os.path.join(path1, path2)

    @staticmethod   
    def write_json_to_file(file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return
    
    @staticmethod
    def read_json_from_file(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
