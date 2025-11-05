import os

class FileManager:
    def __init__(self, root_path="."):
        self.root_path = os.path.abspath(root_path)

    def list_files(self):
        """Return list of files in the current directory."""
        files = []
        for root, _, filenames in os.walk(self.root_path):
            for file in filenames:
                files.append(os.path.join(root, file))
        return files
