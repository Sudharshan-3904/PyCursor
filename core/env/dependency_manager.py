import os

class DependencyManager:
    def __init__(self, project_path):
        self.project_path = project_path

    def detect_requirements(self):
        found = []
        if not self.project_path:
            return found
            
        req_file = os.path.join(self.project_path, "requirements.txt")
        pyproject = os.path.join(self.project_path, "pyproject.toml")
        
        if os.path.exists(req_file):
            found.append("requirements.txt")
        if os.path.exists(pyproject):
            found.append("pyproject.toml")
        return found

    def get_install_command(self, python_path, file_name):
        full_path = os.path.join(self.project_path, file_name)
        if file_name == "requirements.txt":
            return [python_path, "-m", "pip", "install", "-r", full_path]
        elif file_name == "pyproject.toml":
             # Basic install for now, assumes pip can handle it
             return [python_path, "-m", "pip", "install", "."]
        return None
