import os
import sys
import venv
import subprocess
import platform

class EnvironmentManager:
    def __init__(self, project_path=None):
        self.project_path = project_path
        self._active_env = None

    def set_project_path(self, path):
        self.project_path = path

    def list_environments(self):
        """Detect common virtual environment directories."""
        envs = []
        
        # Always include System Python
        envs.append({
            "name": "Global Python",
            "path": sys.executable,
            "type": "system"
        })

        if not self.project_path or not os.path.isdir(self.project_path):
            return envs
        
        # Check for local venvs
        common_names = [".venv", "venv", "env", ".env", "env3"]
        
        try:
            with os.scandir(self.project_path) as it:
                for entry in it:
                    if entry.is_dir() and entry.name in common_names:
                        python_path = self._get_python_executable(entry.path)
                        if python_path and os.path.exists(python_path):
                            envs.append({
                                "name": entry.name,
                                "path": python_path,
                                "type": "venv"
                            })
        except Exception as e:
            print(f"Error scanning for environments: {e}")
        
        return envs

    def _get_python_executable(self, env_dir):
        if platform.system() == "Windows":
            return os.path.join(env_dir, "Scripts", "python.exe")
        else:
            return os.path.join(env_dir, "bin", "python")

    def create_venv(self, name=".venv"):
        if not self.project_path:
            raise ValueError("Project path not set")
        
        env_dir = os.path.join(self.project_path, name)
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(env_dir)
        return self._get_python_executable(env_dir)

    def get_active_env(self):
        if self._active_env and os.path.exists(self._active_env):
            return self._active_env
        return sys.executable  # Fallback to system python

    def set_active_env(self, python_path):
        if os.path.exists(python_path):
            self._active_env = python_path

    def get_installed_packages(self, python_path):
        """Run pip freeze on the given python executable."""
        try:
            # Need to create startupinfo to hide window on Windows
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            result = subprocess.run(
                [python_path, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True,
                startupinfo=startupinfo
            )
            return result.stdout.splitlines()
        except subprocess.CalledProcessError:
            return []
        except Exception:
            return []
