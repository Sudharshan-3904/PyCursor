"""
Keybindings Settings Dialog

Allows users to view and customize keyboard shortcuts.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QHeaderView, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from core.ui.theme import COLORS


class KeybindingsDialog(QDialog):
    """Dialog for viewing and editing keyboard shortcuts"""
    
    def __init__(self, parent=None, keybindings_manager=None):
        super().__init__(parent)
        self.keybindings_manager = keybindings_manager
        self.setWindowTitle("Keyboard Shortcuts")
        self.resize(800, 600)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['list_hover']};
                color: {COLORS['text_highlight']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {COLORS['button_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['button_active']};
            }}
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 6px;
                border-radius: 4px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['border_focus']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Title
        title = QLabel("Keyboard Shortcuts")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by command or shortcut...")
        self.search_input.textChanged.connect(self.filter_shortcuts)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Category", "Command", "Shortcut", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Populate table
        self.populate_table()
    
    def populate_table(self):
        """Populate the table with all keybindings"""
        self.table.setRowCount(0)
        
        if not self.keybindings_manager:
            return
        
        categorized = self.keybindings_manager.get_all_keybindings()
        
        row = 0
        for category in sorted(categorized.keys()):
            bindings = categorized[category]
            for binding in sorted(bindings, key=lambda x: x['description']):
                self.table.insertRow(row)
                
                # Category
                category_item = QTableWidgetItem(category)
                category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, category_item)
                
                # Command
                command_item = QTableWidgetItem(binding['description'])
                command_item.setData(Qt.ItemDataRole.UserRole, binding['id'])
                command_item.setFlags(command_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, command_item)
                
                # Shortcut
                shortcut_item = QTableWidgetItem(binding['key'])
                shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, shortcut_item)
                
                # Edit button
                edit_btn = QPushButton("Edit")
                edit_btn.setProperty("action_id", binding['id'])
                edit_btn.clicked.connect(lambda checked, aid=binding['id']: self.edit_shortcut(aid))
                
                # Create a widget to center the button
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.addWidget(edit_btn)
                button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                button_layout.setContentsMargins(4, 4, 4, 4)
                
                self.table.setCellWidget(row, 3, button_widget)
                
                row += 1
    
    def filter_shortcuts(self, text):
        """Filter shortcuts based on search text"""
        text = text.lower()
        for row in range(self.table.rowCount()):
            command_item = self.table.item(row, 1)
            shortcut_item = self.table.item(row, 2)
            
            if command_item and shortcut_item:
                command = command_item.text().lower()
                shortcut = shortcut_item.text().lower()
                
                if text in command or text in shortcut:
                    self.table.setRowHidden(row, False)
                else:
                    self.table.setRowHidden(row, True)
    
    def edit_shortcut(self, action_id):
        """Edit a keyboard shortcut"""
        current_key = self.keybindings_manager.get(action_id)
        description = self.keybindings_manager.get_description(action_id)
        
        # Create input dialog
        dialog = KeySequenceDialog(self, description, current_key)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_key = dialog.get_key_sequence()
            
            if new_key:
                # Check for conflicts
                conflicts = self.keybindings_manager.check_conflicts(new_key, action_id)
                if conflicts:
                    conflict_names = [self.keybindings_manager.get_description(c) for c in conflicts]
                    reply = QMessageBox.question(
                        self,
                        "Shortcut Conflict",
                        f"This shortcut is already used by:\n{', '.join(conflict_names)}\n\nDo you want to reassign it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Update the shortcut
                self.keybindings_manager.update_shortcut(action_id, new_key)
                self.keybindings_manager.save_bindings()
                
                # Refresh the table
                self.populate_table()
                
                QMessageBox.information(
                    self,
                    "Shortcut Updated",
                    f"Shortcut for '{description}' has been updated.\n\nRestart the application for changes to take full effect."
                )
    
    def reset_to_defaults(self):
        """Reset all keybindings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all keyboard shortcuts to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear custom bindings file
            import os
            if os.path.exists(self.keybindings_manager.config_path):
                os.remove(self.keybindings_manager.config_path)
            
            # Reload bindings
            self.keybindings_manager.bindings = self.keybindings_manager.load_bindings()
            
            # Refresh table
            self.populate_table()
            
            QMessageBox.information(
                self,
                "Reset Complete",
                "All keyboard shortcuts have been reset to defaults.\n\nRestart the application for changes to take full effect."
            )


class KeySequenceDialog(QDialog):
    """Dialog for capturing a key sequence"""
    
    def __init__(self, parent=None, command_name="", current_key=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Keyboard Shortcut")
        self.resize(400, 150)
        self.key_sequence = current_key
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {COLORS['button_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Command name
        label = QLabel(f"Enter new shortcut for: {command_name}")
        layout.addWidget(label)
        
        # Key input
        self.key_input = QLineEdit()
        self.key_input.setText(current_key)
        self.key_input.setPlaceholderText("Press keys to set shortcut...")
        self.key_input.setReadOnly(True)
        layout.addWidget(self.key_input)
        
        # Instructions
        instructions = QLabel("Press the key combination you want to use.\nPress Escape to cancel.")
        instructions.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_shortcut)
        button_layout.addWidget(clear_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def keyPressEvent(self, event):
        """Capture key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        
        # Build key sequence string
        modifiers = event.modifiers()
        key = event.key()
        
        # Skip modifier-only presses
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("Meta")
        
        # Add the key
        key_text = QKeySequence(key).toString()
        if key_text:
            parts.append(key_text)
        
        self.key_sequence = "+".join(parts)
        self.key_input.setText(self.key_sequence)
    
    def clear_shortcut(self):
        """Clear the shortcut"""
        self.key_sequence = ""
        self.key_input.setText("")
    
    def get_key_sequence(self):
        """Get the captured key sequence"""
        return self.key_sequence
