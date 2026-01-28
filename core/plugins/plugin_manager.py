"""
Dynamic Plugin Architecture Module for PyCursor IDE.
Manages the discovery, automated loading, and lifecycle state of third-party Python plugins.
Provides a standardized activation contract for extending IDE functionality.
"""

import os
import importlib.util
import sys
import json
from PyQt6.QtCore import QObject, pyqtSignal

class PluginManager(QObject):
    """
    Registry and loader for PyCursor IDE plugins.
    Plugins are expected to be isolated directories containing a 'main.py' entry point
    with 'activate' and optional 'deactivate' hooks.
    """
    plugin_loaded = pyqtSignal(str)   # Logic: emitted when a plugin is successfully activated
    plugin_error = pyqtSignal(str, str) # Logic: emitted with (plugin_id, error_message)

    def __init__(self, main_window):
        """
        Initializes the manager and resolves the singleton plugins directory.
        """
        super().__init__()
        self.main_window = main_window
        # Resolve path to the 'plugins' directory at the project root
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.plugins_dir = os.path.join(root, "plugins")
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.active_plugins = {}

    def discover_plugins(self) -> list:
        """
        Scans the plugin root for subdirectory-based packages containing a valid plugin.json.
        """
        manifests = []
        try:
            for item in os.listdir(self.plugins_dir):
                path = os.path.join(self.plugins_dir, item)
                manifest = os.path.join(path, "plugin.json")
                if os.path.isdir(path) and os.path.exists(manifest):
                    with open(manifest, 'r', encoding='utf-8') as f:
                        manifests.append(json.load(f))
        except (IOError, json.JSONDecodeError):
            pass
        return manifests

    def load_plugin(self, folder_name: str) -> tuple:
        """
        Dynamically imports a plugin module and executes its activation hook.
        Returns a (success_bool, message) tuple.
        """
        if folder_name in self.active_plugins:
            return True, "Plugin is already active."

        entry_point = os.path.join(self.plugins_dir, folder_name, "main.py")
        if not os.path.exists(entry_point):
            return False, "Main entry point (main.py) not found."

        try:
            # Create a module spec from the target file location
            module_id = f"plugins.ext_{folder_name}"
            spec = importlib.util.spec_from_file_location(module_id, entry_point)
            module = importlib.util.module_from_spec(spec)
            
            # Persist in sys.modules and execute the module body
            sys.modules[module_id] = module
            spec.loader.exec_module(module)

            # Execution Contract: Plugins must expose an 'activate' function
            if hasattr(module, "activate"):
                module.activate(self.main_window)
                self.active_plugins[folder_name] = module
                self.plugin_loaded.emit(folder_name)
                return True, "Activation successful."
            
            return False, "Module does not implement the 'activate' hook."
            
        except Exception as e:
            self.plugin_error.emit(folder_name, str(e))
            return False, f"Activation runtime error: {e}"

    def unload_plugin(self, folder_name: str) -> bool:
        """
        Deactivates an active plugin by calling its 'deactivate' hook and removing it from the registry.
        """
        if folder_name in self.active_plugins:
            module = self.active_plugins.pop(folder_name)
            if hasattr(module, "deactivate"):
                try:
                    module.deactivate(self.main_window)
                except Exception:
                    pass # Ensure failure in deactivation doesn't block IDE cleanup
            return True
        return False

    def load_all_plugins(self):
        """
        Automated iteration and loading of all discoverable plugins.
        """
        for item in os.listdir(self.plugins_dir):
            if os.path.isdir(os.path.join(self.plugins_dir, item)):
                self.load_plugin(item)
