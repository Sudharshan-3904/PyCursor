import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, 
    QPushButton, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox, 
    QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from core.utilities.utils import load_icon
from core.ui.theme import COLORS

from core.extensions.extension_manager import ExtensionManager

class ExtensionsPanel(QWidget):
    """
    Panel for managing extensions (VS Code style).
    Allows installing .vsix files and managing installed extensions.
    """
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.manager = ExtensionManager()
        self.setup_ui()
        self.load_extensions()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 5)
        
        title = QLabel("EXTENSIONS")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_secondary']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Install Button (Three dots style usually, but explicit here for clarity)
        install_btn = QPushButton("...")
        install_btn.setToolTip("Install from VSIX...")
        install_btn.setFixedSize(25, 25)
        install_btn.clicked.connect(self.install_from_vsix)
        header_layout.addWidget(install_btn)
        
        layout.addWidget(header)

        # Search Bar
        search_container = QWidget()
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 10)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Extensions...")
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                padding: 5px;
                color: {COLORS['text_primary']};
                border-radius: 4px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['accent_blue']};
            }}
        """)
        self.search_bar.textChanged.connect(self.filter_extensions)
        search_layout.addWidget(self.search_bar)
        layout.addWidget(search_container)

        # Extension List
        self.extension_list = QListWidget()
        self.extension_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
        """)
        layout.addWidget(self.extension_list)

    def load_extensions(self):
        """Load installed extensions into the list"""
        self.extension_list.clear()
        
        extensions = self.manager.get_installed_extensions()
        for ext in extensions:
            self.add_extension_item(
                ext['name'], 
                ext['publisher'], 
                ext['description'], 
                True
            )
            
        # Add some "Recommended" placeholders if empty (optional)
        if not extensions:
            self.add_extension_item("Python (Placeholder)", "Microsoft", "Example extension item", False)

    def add_extension_item(self, name, author, description, installed):
        item = QListWidgetItem()
        widget = ExtensionItemWidget(name, author, description, installed)
        item.setSizeHint(widget.sizeHint())
        self.extension_list.addItem(item)
        self.extension_list.setItemWidget(item, widget)

    def filter_extensions(self, text):
        count = self.extension_list.count()
        text = text.lower()
        for i in range(count):
            item = self.extension_list.item(i)
            widget = self.extension_list.itemWidget(item)
            if hasattr(widget, 'name'):
                if text in widget.name.lower() or text in widget.description.lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def install_from_vsix(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Install Extension from VSIX", 
            os.path.expanduser("~"), 
            "VSIX Files (*.vsix)"
        )
        if file_path:
            success, msg = self.manager.install_vsix(file_path)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_extensions()
            else:
                QMessageBox.critical(self, "Error", f"Failed to install: {msg}")

class ExtensionItemWidget(QWidget):
    def __init__(self, name, author, description, installed):
        super().__init__()
        self.name = name
        self.author = author
        self.description = description
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Icon placeholder
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border-radius: 4px;")
        layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']}; font-size: 11px;")
        info_layout.addWidget(name_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        author_label = QLabel(author)
        author_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-size: 9px;")
        info_layout.addWidget(author_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        if not installed:
            install_btn = QPushButton("Install")
            install_btn.setStyleSheet(f"""
                background-color: {COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 2px;
                padding: 4px 8px;
            """)
            layout.addWidget(install_btn)
