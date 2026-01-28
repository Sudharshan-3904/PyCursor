import os
import importlib.util
import sys
import json
from PyQt6.QtCore import QObject, pyqtSignal

class PluginManager(QObject):
    """
    Manages loading and lifecycle of Python-based plugins for PyCursor.
    Each plugin is a directory in 'plugins/' containing an '__init__.py' or a specified entry point.
    """
    plugin_loaded = pyqtSignal(str)
    plugin_error = pyqtSignal(str, str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.plugins_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins")
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.active_plugins = {}

    def discover_plugins(self):
        """Scan the plugins directory for available plugins."""
        plugins = []
        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)
            if os.path.isdir(item_path):
                # Check for manifest or __init__.py
                manifest_path = os.path.join(item_path, "plugin.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            plugins.append(json.load(f))
                    except:
                        pass
        return plugins

    def load_plugin(self, plugin_folder_name):
        """Dynamically load and activate a plugin."""
        if plugin_folder_name in self.active_plugins:
            return True, "Plugin already loaded"

        plugin_path = os.path.join(self.plugins_dir, plugin_folder_name)
        entry_point = os.path.join(plugin_path, "main.py")
        
        if not os.path.exists(entry_point):
            return False, f"Entry point {entry_point} not found"

        try:
            module_name = f"plugins.{plugin_folder_name}"
            spec = importlib.util.spec_from_file_location(module_name, entry_point)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, "activate"):
                module.activate(self.main_window)
                self.active_plugins[plugin_folder_name] = module
                self.plugin_loaded.emit(plugin_folder_name)
                return True, "Success"
            else:
                return False, "Plugin has no 'activate' function"
        except Exception as e:
            self.plugin_error.emit(plugin_folder_name, str(e))
            return False, str(e)

    def unload_plugin(self, plugin_folder_name):
        """Deactivate and unload a plugin."""
        if plugin_folder_name in self.active_plugins:
            module = self.active_plugins[plugin_folder_name]
            if hasattr(module, "deactivate"):
                try:
                    module.deactivate(self.main_window)
                except:
                    pass
            del self.active_plugins[plugin_folder_name]
            # Note: Truly unloading from sys.modules is tricky in Python
            return True
        return False

    def load_all_plugins(self):
        """Load all plugins found in the plugins directory."""
        for item in os.listdir(self.plugins_dir):
            if os.path.isdir(os.path.join(self.plugins_dir, item)):
                self.load_plugin(item)
