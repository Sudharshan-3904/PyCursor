"""
Keybindings Manager for PyCursor IDE

This module provides a centralized system for managing keyboard shortcuts.
It allows for easy configuration, customization, and conflict detection.
"""

import json
import os
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from typing import Dict, Callable, Optional, List

# Default keybindings with metadata
DEFAULT_KEYBINDINGS = {
    # File Operations
    "file.open": {
        "key": "Ctrl+O",
        "description": "Open File",
        "category": "File"
    },
    "file.open_folder": {
        "key": "Ctrl+K Ctrl+O",
        "description": "Open Folder",
        "category": "File"
    },
    "file.save": {
        "key": "Ctrl+S",
        "description": "Save File",
        "category": "File"
    },
    "file.save_as": {
        "key": "Ctrl+Shift+S",
        "description": "Save As",
        "category": "File"
    },
    "file.close_tab": {
        "key": "Ctrl+W",
        "description": "Close Tab",
        "category": "File"
    },
    "file.new_file": {
        "key": "Ctrl+N",
        "description": "New File",
        "category": "File"
    },
    
    # Edit Operations
    "edit.undo": {
        "key": "Ctrl+Z",
        "description": "Undo",
        "category": "Edit"
    },
    "edit.redo": {
        "key": "Ctrl+Y",
        "description": "Redo",
        "category": "Edit"
    },
    "edit.cut": {
        "key": "Ctrl+X",
        "description": "Cut",
        "category": "Edit"
    },
    "edit.copy": {
        "key": "Ctrl+C",
        "description": "Copy",
        "category": "Edit"
    },
    "edit.paste": {
        "key": "Ctrl+V",
        "description": "Paste",
        "category": "Edit"
    },
    "edit.find": {
        "key": "Ctrl+F",
        "description": "Find",
        "category": "Edit"
    },
    "edit.find_in_files": {
        "key": "Ctrl+Shift+F",
        "description": "Find in Files",
        "category": "Edit"
    },
    "edit.replace": {
        "key": "Ctrl+H",
        "description": "Replace",
        "category": "Edit"
    },
    "edit.select_all": {
        "key": "Ctrl+A",
        "description": "Select All",
        "category": "Edit"
    },
    "edit.toggle_comment": {
        "key": "Ctrl+/",
        "description": "Toggle Line Comment",
        "category": "Edit"
    },
    "edit.duplicate_line": {
        "key": "Ctrl+D",
        "description": "Duplicate Line",
        "category": "Edit"
    },
    "edit.delete_line": {
        "key": "Ctrl+Shift+K",
        "description": "Delete Line",
        "category": "Edit"
    },
    "edit.move_line_up": {
        "key": "Alt+Up",
        "description": "Move Line Up",
        "category": "Edit"
    },
    "edit.move_line_down": {
        "key": "Alt+Down",
        "description": "Move Line Down",
        "category": "Edit"
    },
    
    # View Operations
    "view.toggle_explorer": {
        "key": "Ctrl+B",
        "description": "Toggle Explorer",
        "category": "View"
    },
    "view.toggle_terminal": {
        "key": "Ctrl+`",
        "description": "Toggle Terminal",
        "category": "View"
    },
    "view.toggle_ai": {
        "key": "Ctrl+Shift+A",
        "description": "Toggle AI Assistant",
        "category": "View"
    },
    "view.zoom_in": {
        "key": "Ctrl++",
        "description": "Zoom In",
        "category": "View"
    },
    "view.zoom_out": {
        "key": "Ctrl+-",
        "description": "Zoom Out",
        "category": "View"
    },
    "view.reset_zoom": {
        "key": "Ctrl+0",
        "description": "Reset Zoom",
        "category": "View"
    },
    
    # Navigation
    "navigation.go_to_line": {
        "key": "Ctrl+G",
        "description": "Go to Line",
        "category": "Navigation"
    },
    "navigation.next_tab": {
        "key": "Ctrl+Tab",
        "description": "Next Tab",
        "category": "Navigation"
    },
    "navigation.previous_tab": {
        "key": "Ctrl+Shift+Tab",
        "description": "Previous Tab",
        "category": "Navigation"
    },
    "navigation.go_to_definition": {
        "key": "F12",
        "description": "Go to Definition",
        "category": "Navigation"
    },
    "navigation.go_back": {
        "key": "Alt+Left",
        "description": "Go Back",
        "category": "Navigation"
    },
    "navigation.go_forward": {
        "key": "Alt+Right",
        "description": "Go Forward",
        "category": "Navigation"
    },
    
    # Run/Debug
    "run.run_code": {
        "key": "Ctrl+Shift+R",
        "description": "Run File",
        "category": "Run"
    },
    "run.debug": {
        "key": "F5",
        "description": "Start Debugging",
        "category": "Run"
    },
    "run.stop": {
        "key": "Shift+F5",
        "description": "Stop Debugging",
        "category": "Run"
    },
    
    # AI Features
    "ai.chat": {
        "key": "Ctrl+Shift+I",
        "description": "Open AI Chat",
        "category": "AI"
    },
    "ai.explain_code": {
        "key": "Ctrl+Shift+E",
        "description": "Explain Selected Code",
        "category": "AI"
    },
    
    # Terminal
    "terminal.new": {
        "key": "Ctrl+Shift+`",
        "description": "New Terminal",
        "category": "Terminal"
    },
    "terminal.clear": {
        "key": "Ctrl+K",
        "description": "Clear Terminal",
        "category": "Terminal"
    },
    
    # Application
    "app.quick_open": {
        "key": "Ctrl+P",
        "description": "Quick Open File",
        "category": "Application"
    },
    "app.command_palette": {
        "key": "Ctrl+Shift+P",
        "description": "Show Command Palette",
        "category": "Application"
    },
    "app.settings": {
        "key": "Ctrl+,",
        "description": "Open Settings",
        "category": "Application"
    },
}


class KeyBindingsManager:
    """Singleton manager for keyboard shortcuts"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyBindingsManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Initialize the keybindings manager"""
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config", "keybindings.json"
        )
        self.bindings = self.load_bindings()
        self.shortcuts: Dict[str, QShortcut] = {}

    def load_bindings(self):
        """Load keybindings from config file, merging with defaults"""
        bindings = {}
        
        # Start with defaults
        for action_id, config in DEFAULT_KEYBINDINGS.items():
            bindings[action_id] = config.copy()
        
        # Load and merge custom bindings
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_bindings = json.load(f)
                    for action_id, config in user_bindings.items():
                        if action_id in bindings:
                            # Update existing binding
                            bindings[action_id].update(config)
                        else:
                            # Add new custom binding
                            bindings[action_id] = config
        except Exception as e:
            print(f"Error loading keybindings: {e}")
        
        return bindings

    def save_bindings(self):
        """Save current keybindings to config file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.bindings, f, indent=2)
        except Exception as e:
            print(f"Error saving keybindings: {e}")

    def get(self, action_id: str) -> str:
        """Get the key sequence string for an action"""
        binding = self.bindings.get(action_id, {})
        if isinstance(binding, dict):
            return binding.get("key", "")
        return binding  # Backward compatibility with old format

    def set(self, action_id: str, sequence: str):
        """Set a new key sequence for an action"""
        if action_id in self.bindings:
            if isinstance(self.bindings[action_id], dict):
                self.bindings[action_id]["key"] = sequence
            else:
                # Convert old format to new format
                self.bindings[action_id] = {
                    "key": sequence,
                    "description": action_id.split(".")[-1].replace("_", " ").title(),
                    "category": action_id.split(".")[0].title()
                }
        else:
            self.bindings[action_id] = {
                "key": sequence,
                "description": action_id.split(".")[-1].replace("_", " ").title(),
                "category": action_id.split(".")[0].title()
            }
        self.save_bindings()

    def get_sequence(self, action_id: str) -> QKeySequence:
        """Get QKeySequence object for an action"""
        shortcut = self.get(action_id)
        return QKeySequence(shortcut) if shortcut else QKeySequence()

    def register_shortcut(self, action_id: str, callback: Callable, context) -> Optional[QShortcut]:
        """
        Register a keyboard shortcut with a callback
        
        Args:
            action_id: Unique identifier for the action
            callback: Function to call when shortcut is triggered
            context: Widget context for the shortcut
            
        Returns:
            QShortcut object or None if registration failed
        """
        if action_id not in self.bindings:
            print(f"Warning: Unknown action_id '{action_id}'")
            return None
        
        key_sequence = self.get(action_id)
        if not key_sequence:
            return None
        
        # Create shortcut
        shortcut = QShortcut(QKeySequence(key_sequence), context)
        shortcut.activated.connect(callback)
        
        # Store reference
        self.shortcuts[action_id] = shortcut
        
        return shortcut

    def unregister_shortcut(self, action_id: str):
        """Unregister a keyboard shortcut"""
        if action_id in self.shortcuts:
            self.shortcuts[action_id].setEnabled(False)
            del self.shortcuts[action_id]

    def update_shortcut(self, action_id: str, new_key: str) -> bool:
        """Update a keyboard shortcut"""
        self.set(action_id, new_key)
        
        # Update active shortcut if it exists
        if action_id in self.shortcuts:
            self.shortcuts[action_id].setKey(QKeySequence(new_key))
        
        return True

    def get_description(self, action_id: str) -> str:
        """Get description for an action"""
        binding = self.bindings.get(action_id, {})
        if isinstance(binding, dict):
            return binding.get("description", "")
        return ""

    def get_category(self, action_id: str) -> str:
        """Get category for an action"""
        binding = self.bindings.get(action_id, {})
        if isinstance(binding, dict):
            return binding.get("category", "Other")
        return "Other"

    def get_all_keybindings(self) -> Dict[str, List[Dict]]:
        """Get all keybindings organized by category"""
        categorized = {}
        for action_id, binding in self.bindings.items():
            if isinstance(binding, dict):
                category = binding.get("category", "Other")
                key = binding.get("key", "")
                description = binding.get("description", "")
            else:
                # Old format
                category = "Other"
                key = binding
                description = action_id
            
            if category not in categorized:
                categorized[category] = []
            
            categorized[category].append({
                "id": action_id,
                "key": key,
                "description": description,
            })
        
        return categorized

    def check_conflicts(self, key_sequence: str, exclude_action: str = None) -> List[str]:
        """Check if a key sequence conflicts with existing bindings"""
        conflicts = []
        for action_id, binding in self.bindings.items():
            if action_id == exclude_action:
                continue
            
            existing_key = binding.get("key", "") if isinstance(binding, dict) else binding
            if existing_key == key_sequence:
                conflicts.append(action_id)
        
        return conflicts

    def disable_shortcut(self, action_id: str):
        """Temporarily disable a shortcut"""
        if action_id in self.shortcuts:
            self.shortcuts[action_id].setEnabled(False)

    def enable_shortcut(self, action_id: str):
        """Re-enable a disabled shortcut"""
        if action_id in self.shortcuts:
            self.shortcuts[action_id].setEnabled(True)
