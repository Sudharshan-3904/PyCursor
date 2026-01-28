"""
Python Environment and Virtualenv Management Module.
Handles discovery, creation, and inspection of Python runtimes within the project scope.
Ensures that the IDE correctly identifies and utilizes project-specific dependencies.
"""

import os
import sys
import venv
import subprocess
import platform

class EnvironmentManager:
    """
    Manages Python interpreters and virtual environments associated with the active project.
    Provides utilities to list available runtimes and create new isolated environments.
    """
    def __init__(self, project_path=None):
        """
        Initializes the manager with an optional project root.
        """
        self.project_path = project_path
        self._active_env = None

    def set_project_path(self, path: str):
        """
        Updates the target project directory for environment discovery.
        """
        self.project_path = path

    def list_environments(self) -> list:
        """
        Scans the project directory and system for valid Python runtimes.
        Returns a list of dictionaries containing name, absolute path, and runtime type.
        """
        envs = []
        
        # 1. System Default Interpreter
        envs.append({
            "name": "Global Python",
            "path": sys.executable,
            "type": "system"
        })

        if not self.project_path or not os.path.isdir(self.project_path):
            return envs
        
        # 2. Heuristic Search for Local Virtual Environments
        venv_names = [".venv", "venv", "env", ".env", "env3"]
        try:
            for entry in os.scandir(self.project_path):
                if entry.is_dir() and entry.name in venv_names:
                    binary_path = self._resolve_python_binary(entry.path)
                    if binary_path and os.path.exists(binary_path):
                        envs.append({
                            "name": entry.name,
                            "path": binary_path,
                            "type": "venv"
                        })
        except Exception:
            pass
        
        return envs

    def _resolve_python_binary(self, env_dir: str) -> str:
        """
        Platform-aware resolution of the Python executable within a virtual environment directory.
        """
        if platform.system() == "Windows":
            return os.path.join(env_dir, "Scripts", "python.exe")
        return os.path.join(env_dir, "bin", "python")

    def create_venv(self, name: str = ".venv") -> str:
        """
        Programmatically creates a new isolated virtual environment using the standard library.
        """
        if not self.project_path: raise ValueError("Target project path must be set.")
        
        target_dir = os.path.join(self.project_path, name)
        # Initialize the environment with pip pre-installed
        venv.EnvBuilder(with_pip=True).create(target_dir)
        return self._resolve_python_binary(target_dir)

    def get_active_env(self) -> str:
        """
        Returns the path to the currently selected Python interpreter.
        Defaults to the global system Python if no project-specific env is active.
        """
        return self._active_env if (self._active_env and os.path.exists(self._active_env)) else sys.executable

    def set_active_env(self, python_path: str):
        """
        Persists the path to the chosen interpreter for the current session.
        """
        if os.path.exists(python_path):
            self._active_env = python_path

    def get_installed_packages(self, python_path: str) -> list:
        """
        Queries the provided interpreter for its currently installed package manifest via 'pip freeze'.
        """
        try:
            # Hide the subprocess console window on Windows
            si = None
            if platform.system() == "Windows":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            res = subprocess.run(
                [python_path, "-m", "pip", "freeze"],
                capture_output=True, text=True, check=True, startupinfo=si
            )
            return res.stdout.splitlines()
        except Exception:
            return []
