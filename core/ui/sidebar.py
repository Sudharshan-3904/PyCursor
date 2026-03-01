from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeView,
    QHBoxLayout, QPushButton, QComboBox, QSizePolicy, QLineEdit, QMenu, QApplication
)
from PyQt6.QtGui import QFileSystemModel, QAction
from PyQt6.QtCore import pyqtSignal, QModelIndex, QSortFilterProxyModel, Qt

import os
import shutil
from core.utilities.utils import load_icon

class SideBar(QWidget):
    """
    Primary project navigation component providing file tree exploration,
    file system operations (CRUD), and display filtering.
    """
    file_selected = pyqtSignal(str)
    model_changed = pyqtSignal(str, str)

    def __init__(self, root_path=None):
        """
        Initializes the sidebar with a file system model and UI controls.
        """
        super().__init__()

        self.root_path = root_path or os.getcwd()
        self.creating_item = None
        self.filter_mode = False
        self._init_ui()

    def _init_ui(self):
        """
        Constructs the sidebar layout and widget hierarchy.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)


        # Navigation toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 0, 8, 0)
        toolbar_layout.setSpacing(6)

        self.dir_label = QLabel(os.path.basename(self.root_path))
        self.dir_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Action Buttons
        refresh_btn = self._create_toolbar_button("refresh.png", "Refresh Tree", self.refresh_tree)
        new_file_btn = self._create_toolbar_button("new_file.png", "New File", lambda: self.create_item(is_folder=False))
        new_folder_btn = self._create_toolbar_button("new_folder.png", "New Folder", lambda: self.create_item(is_folder=True))
        
        self.filter_btn = self._create_toolbar_button("filter.png", "Filter Files", self.toggle_filter)
        self.filter_btn.setCheckable(True)

        self.toolbar_buttons = {"refresh": refresh_btn, "new_file": new_file_btn, "new_folder": new_folder_btn, "filter": self.filter_btn}
        
        toolbar_layout.addWidget(self.dir_label)
        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addWidget(new_file_btn)
        toolbar_layout.addWidget(new_folder_btn)
        toolbar_layout.addWidget(self.filter_btn)
        layout.addWidget(toolbar)

        # File type filter selection
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Show All",
            "Python Files (*.py)",
            "Text Files (*.txt)",
            "JSON Files (*.json)",
            "Python + Text (*.py, *.txt)",
            "Config Files (*.json, *.yaml, *.yml)"
        ])
        self.filter_combo.setVisible(False)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_combo)

        # File system integration
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root_path)

        self.proxy_model = ExtensionFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        root_index = self.model.index(self.root_path)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(root_index))
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.tree.clicked.connect(self.on_item_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.tree)

    def _create_toolbar_button(self, icon_name, tooltip, callback):
        """
        Helper to create uniform toolbar buttons.
        """
        btn = QPushButton()
        btn.setIcon(load_icon(icon_name))
        btn.setToolTip(tooltip)
        btn.setFixedSize(20, 20)
        btn.clicked.connect(callback)
        return btn

    def refresh_tree(self):
        """
        Synchronizes the view with the current file system state.
        Ensures the root index is correctly set.
        """
        root_index = self.model.index(self.root_path)
        proxy_root = self.proxy_model.mapFromSource(root_index)
        if self.tree.rootIndex() != proxy_root:
            self.tree.setRootIndex(proxy_root)

    def set_root_path(self, path: str):
        """
        Updates the active project root directory.
        """
        if not path: return
        self.root_path = path
        self.dir_label.setText(os.path.basename(self.root_path) or self.root_path)
        self.model.setRootPath(self.root_path)
        self.refresh_tree()

    def refresh_icons(self, theme_name):
        """
        Updates toolbar icons to match the current theme color.
        """
        from core.ui.theme import get_icon_color
        color = get_icon_color(theme_name)
        
        icon_map = {
            "refresh": "refresh.png",
            "new_file": "new_file.png",
            "new_folder": "new_folder.png",
            "filter": "filter.png"
        }
        
        for key, btn in self.toolbar_buttons.items():
            if key in icon_map:
                btn.setIcon(load_icon(icon_map[key], color=color))

    def toggle_filter(self):
        """
        Visually toggles the file extension filter dropdown.
        """
        self.filter_mode = self.filter_btn.isChecked()
        self.filter_combo.setVisible(self.filter_mode)

    def apply_filter(self):
        """
        Applies extension-based filtering to the file tree.
        """
        selected = self.filter_combo.currentText()
        ext_map = {
            "Python Files": [".py"],
            "Text Files": [".txt"],
            "JSON Files": [".json"],
            "Python + Text": [".py", ".txt"],
            "Config Files": [".json", ".yaml", ".yml"]
        }
        exts = []
        for key, val in ext_map.items():
            if key in selected: exts = val
        self.proxy_model.setAllowedExtensions(exts)

    def on_item_clicked(self, index: QModelIndex):
        """
        Emits selection signal for files; toggles expansion for directories.
        """
        source_index = self.proxy_model.mapToSource(index)
        if self.model.isDir(source_index):
            if self.tree.isExpanded(index):
                self.tree.collapse(index)
            else:
                self.tree.expand(index)
        else:
            self.file_selected.emit(self.model.filePath(source_index))

    def create_item(self, is_folder=False):
        """
        Initiates the creation of a new file or folder with an inline editor.
        """
        if self.creating_item: return

        parent_index = self.tree.rootIndex()
        parent_path = self.model.filePath(self.proxy_model.mapToSource(parent_index))
        temp_name = "New Folder" if is_folder else "New File"
        
        # Ensure unique temporary name
        target_path = os.path.join(parent_path, temp_name)
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join(parent_path, f"{temp_name} {counter}")
            counter += 1

        self.creating_item = QLineEdit(os.path.basename(target_path), self.tree)
        self.creating_item.setFrame(False)
        self.creating_item.setGeometry(25, 25, 200, 22)
        self.creating_item.setFocus()
        self.creating_item.selectAll()
        self.creating_item.show()

        self.creating_item.returnPressed.connect(lambda: self.finalize_creation(parent_path, is_folder))
        self.creating_item.editingFinished.connect(self.cancel_creation)

    def finalize_creation(self, parent_path, is_folder):
        """
        Writes the new item to disk.
        """
        name = self.creating_item.text().strip()
        if not name:
            self.cancel_creation()
            return

        new_path = os.path.join(parent_path, name)
        try:
            if is_folder:
                os.makedirs(new_path, exist_ok=False)
            else:
                with open(new_path, "w") as f: f.write("")
        except Exception: pass

        self._cleanup_creator()
        self.refresh_tree()

    def cancel_creation(self):
        """
        Aborts the pending creation operation.
        """
        self._cleanup_creator()

    def _cleanup_creator(self):
        """
        Removes the temporary creation widget.
        """
        if self.creating_item:
            self.creating_item.deleteLater()
            self.creating_item = None

    def show_context_menu(self, position):
        """
        Displays contextual actions for files and directories.
        """
        index = self.tree.indexAt(position)
        menu = QMenu()
        
        new_file_act = QAction("New File", self)
        new_file_act.triggered.connect(lambda: self.create_item(is_folder=False))
        menu.addAction(new_file_act)
        
        new_folder_act = QAction("New Folder", self)
        new_folder_act.triggered.connect(lambda: self.create_item(is_folder=True))
        menu.addAction(new_folder_act)
        
        if index.isValid():
            menu.addSeparator()
            source_index = self.proxy_model.mapToSource(index)
            file_path = self.model.filePath(source_index)
            
            rename_act = QAction("Rename", self)
            rename_act.triggered.connect(lambda: self.rename_item(index))
            menu.addAction(rename_act)
            
            delete_act = QAction("Delete", self)
            delete_act.triggered.connect(lambda: self.delete_item(index))
            menu.addAction(delete_act)
            
            menu.addSeparator()
            reveal_act = QAction("Reveal in Explorer", self)
            reveal_act.triggered.connect(lambda: os.startfile(os.path.dirname(file_path)))
            menu.addAction(reveal_act)
            
            copy_path_act = QAction("Copy Path", self)
            copy_path_act.triggered.connect(lambda: QApplication.clipboard().setText(file_path))
            menu.addAction(copy_path_act)
        
        menu.exec(self.tree.viewport().mapToGlobal(position))

    def rename_item(self, index):
        """
        Prompts user to rename an existing item.
        """
        source_index = self.proxy_model.mapToSource(index)
        old_path = self.model.filePath(source_index)
        old_name = self.model.fileName(source_index)
        
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh_tree()
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Rename failed: {e}")

    def delete_item(self, index):
        """
        Requests confirmation before permanently deleting an item.
        """
        source_index = self.proxy_model.mapToSource(index)
        file_path = self.model.filePath(source_index)
        
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Permanently delete '{os.path.basename(file_path)}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(file_path): shutil.rmtree(file_path)
                else: os.remove(file_path)
                self.refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}")

class ExtensionFilterProxyModel(QSortFilterProxyModel):
    """
    Subclass of QSortFilterProxyModel to filter file tree based on file extensions.
    """
    def __init__(self):
        super().__init__()
        self.allowed_extensions = []

    def setAllowedExtensions(self, extensions):
        """
        Sets the list of extensions to pass through the filter.
        """
        self.allowed_extensions = [ext.lower() for ext in extensions]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """
        Accepts directories or files with matching extensions.
        """
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid(): return False

        file_path = self.sourceModel().filePath(index)
        if os.path.isdir(file_path): return True
        if not self.allowed_extensions: return True

        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.allowed_extensions
