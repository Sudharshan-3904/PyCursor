from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import os
from core.ui.theme import COLORS
from core.utilities.utils import load_icon

class CommandPalette(QDialog):
    def __init__(self, parent=None, mode="files", project_path=None, actions=None):
        super().__init__(parent)
        self.mode = mode
        self.project_path = project_path
        self.actions = actions or [] # List of (name, callback) tuples
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.resize(600, 400)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_focus']};
            }}
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 8px;
                font-size: 14px;
                border-radius: 4px;
            }}
            QListWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['list_hover']};
                color: {COLORS['text_highlight']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search..." if mode == "files" else "Type a command...")
        self.search_input.textChanged.connect(self.filter_items)
        self.search_input.returnPressed.connect(self.execute_selected)
        layout.addWidget(self.search_input)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.execute_selected)
        layout.addWidget(self.list_widget)
        
        self.items = []
        self.populate_items()
        
        # Focus input
        self.search_input.setFocus()

    def populate_items(self):
        self.list_widget.clear()
        self.items = []
        
        if self.mode == "files" and self.project_path:
            # Walk directory for files
            for root, dirs, files in os.walk(self.project_path):
                if '.git' in dirs: dirs.remove('.git')
                if '__pycache__' in dirs: dirs.remove('__pycache__')
                if 'node_modules' in dirs: dirs.remove('node_modules')
                
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_path)
                    self.items.append((rel_path, full_path))
                    
        elif self.mode == "commands":
            self.items = self.actions

        self.filter_items("")

    def filter_items(self, text):
        self.list_widget.clear()
        text = text.lower()
        
        filtered = []
        for label, data in self.items:
            if text in label.lower():
                filtered.append((label, data))
        
        # Limit results
        for label, data in filtered[:50]:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, data)
            # Add icon based on mode
            if self.mode == "files":
                # Simple icon logic
                if label.endswith('.py'): icon = load_icon("python.svg") # Placeholder
                else: icon = load_icon("file.svg") # Placeholder
                # item.setIcon(icon) # Need actual icons
            
            self.list_widget.addItem(item)
            
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def execute_selected(self):
        if self.list_widget.currentItem():
            data = self.list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
            if self.mode == "files":
                self.parent().open_file_in_tab(data)
            elif self.mode == "commands":
                # data is the callback function
                if callable(data):
                    data()
            self.accept()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            row = self.list_widget.currentRow()
            if row < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(row + 1)
        elif event.key() == Qt.Key.Key_Up:
            row = self.list_widget.currentRow()
            if row > 0:
                self.list_widget.setCurrentRow(row - 1)
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
