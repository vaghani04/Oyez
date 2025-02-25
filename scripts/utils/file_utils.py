import os
import json

class FileUtils:
    def create_directory(self, directory_path):
        os.makedirs(directory_path, exist_ok=True)

    def write_json_file(self, file_path, data):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def write_binary_file(self, file_path, data):
        with open(file_path, "wb") as f:
            f.write(data)

    def write_text_file(self, file_path, text):
        with open(file_path, "w") as f:
            f.write(text)