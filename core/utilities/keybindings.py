"""
Centralized Keybindings Management System for PyCursor IDE.
Provides a registry of default shortcuts, handles user-overrides via JSON persistence,
and manages the lifecycle of QShortcut objects within relevant widget contexts.
"""

import json
import os
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from typing import Dict, Callable, Optional, List

# Dictionary of system-wide default keybindings with metadata.
DEFAULT_KEYBINDINGS = {
    "file.open": {"key": "Ctrl+O", "description": "Open File", "category": "File"},
    "file.open_folder": {"key": "Ctrl+K Ctrl+O", "description": "Open Folder", "category": "File"},
    "file.save": {"key": "Ctrl+S", "description": "Save File", "category": "File"},
    "file.save_as": {"key": "Ctrl+Shift+S", "description": "Save As", "category": "File"},
    "file.close_tab": {"key": "Ctrl+W", "description": "Close Tab", "category": "File"},
    "file.new_file": {"key": "Ctrl+N", "description": "New File", "category": "File"},
    
    "edit.undo": {"key": "Ctrl+Z", "description": "Undo", "category": "Edit"},
    "edit.redo": {"key": "Ctrl+Y", "description": "Redo", "category": "Edit"},
    "edit.cut": {"key": "Ctrl+X", "description": "Cut", "category": "Edit"},
    "edit.copy": {"key": "Ctrl+C", "description": "Copy", "category": "Edit"},
    "edit.paste": {"key": "Ctrl+V", "description": "Paste", "category": "Edit"},
    "edit.find": {"key": "Ctrl+F", "description": "Find", "category": "Edit"},
    "edit.replace": {"key": "Ctrl+H", "description": "Replace", "category": "Edit"},
    "edit.select_all": {"key": "Ctrl+A", "description": "Select All", "category": "Edit"},
    
    "view.toggle_explorer": {"key": "Ctrl+B", "description": "Toggle Explorer", "category": "View"},
    "view.toggle_terminal": {"key": "Ctrl+`", "description": "Toggle Terminal", "category": "View"},
    "view.toggle_ai": {"key": "Ctrl+Shift+A", "description": "Toggle AI Assistant", "category": "View"},
    
    "navigation.go_to_line": {"key": "Ctrl+G", "description": "Go to Line", "category": "Navigation"},
    "run.run_code": {"key": "Ctrl+Shift+R", "description": "Run File", "category": "Run"},
    
    "app.quick_open": {"key": "Ctrl+P", "description": "Quick Open File", "category": "Application"},
    "app.command_palette": {"key": "Ctrl+Shift+P", "description": "Show Command Palette", "category": "Application"},
    "app.settings": {"key": "Ctrl+,", "description": "Open Settings", "category": "Application"},
}

class KeyBindingsManager:
    """
    Singleton manager for defining and registering keyboard shortcuts across the application.
    Supports dynamic re-binding and persistence of user preferences.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyBindingsManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """
        Initializes the manager and loads the binding configuration from the filesystem.
        """
        # Determine path to user-specific keybindings configuration
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_path = os.path.join(root, "config", "keybindings.json")
        self.bindings = self._merge_user_bindings(DEFAULT_KEYBINDINGS.copy())
        self.active_shortcuts: Dict[str, QShortcut] = {}

    def _merge_user_bindings(self, defaults: Dict) -> Dict:
        """
        Internal utility to overlay user-defined shortcuts onto system defaults.
        """
        if not os.path.exists(self.config_path):
            return defaults
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
                for aid, config in user_data.items():
                    if aid in defaults: defaults[aid].update(config)
                    else: defaults[aid] = config
        except Exception as e:
            print(f"I/O Error loading keybindings: {e}")
            
        return defaults

    def save(self):
        """
        Persists the current binding state to the configuration file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.bindings, f, indent=2)
        except Exception as e:
            print(f"Error persisting keybindings: {e}")

    def get(self, action_id: str) -> str:
        """
        Returns the raw string representation (e.g., 'Ctrl+S') for a specific action ID.
        """
        return self.bindings.get(action_id, {}).get("key", "")

    def get_sequence(self, action_id: str) -> QKeySequence:
        """
        Constructs a QKeySequence object for integration with Qt Actions or Widgets.
        """
        seq_str = self.get(action_id)
        return QKeySequence(seq_str) if seq_str else QKeySequence()

    def register(self, action_id: str, callback: Callable, parent) -> Optional[QShortcut]:
        """
        Instantiates and binds a QShortcut to a specific callback within a widget context.
        """
        seq_str = self.get(action_id)
        if not seq_str: return None
        
        shortcut = QShortcut(QKeySequence(seq_str), parent)
        shortcut.activated.connect(callback)
        self.active_shortcuts[action_id] = shortcut
        return shortcut

    def update(self, action_id: str, new_key: str):
        """
        Updates an existing binding and refreshes any active QShortcut objects.
        """
        if action_id in self.bindings:
            self.bindings[action_id]["key"] = new_key
            if action_id in self.active_shortcuts:
                self.active_shortcuts[action_id].setKey(QKeySequence(new_key))
            self.save()

    def get_categorized(self) -> Dict[str, List[Dict]]:
        """
        Groups all current bindings by their category for display in settings menus.
        """
        groups = {}
        for aid, data in self.bindings.items():
            cat = data.get("category", "Other")
            if cat not in groups: groups[cat] = []
            groups[cat].append({"id": aid, "key": data.get("key"), "desc": data.get("description")})
        return groups
