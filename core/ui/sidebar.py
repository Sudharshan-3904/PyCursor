from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeView,
    QHBoxLayout, QPushButton, QComboBox, QSizePolicy, QLineEdit, QMenu
)
from PyQt6.QtGui import QFileSystemModel, QAction
from PyQt6.QtCore import pyqtSignal, QModelIndex, QSortFilterProxyModel

import os
from core.utils import load_icon


class SideBar(QWidget):
    file_selected = pyqtSignal(str)
    model_changed = pyqtSignal(str, str)

    def __init__(self, root_path=None):
        super().__init__()

        self.root_path = root_path or os.getcwd()
        self.creating_item = None
        self.filter_mode = False

        self.models = {
            "LM Studio": ["lm1", "lm2"],
            "Ollama": ["granite", "ruby"],
            "API": ["ChatGPT Go"]
        }
        self.current_model_name = "lm1"
        self.current_backend = "lmstudio"

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)

        header = QLabel("EXPLORER")
        header.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 12px; padding-left: 8px;")
        header.setFixedHeight(20)
        main_layout.addWidget(header)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(8, 0, 8, 0)
        toolbar_layout.setSpacing(6)
        toolbar.setLayout(toolbar_layout)

        self.dir_label = QLabel(os.path.basename(self.root_path))
        self.dir_label.setStyleSheet("color: #dddddd; font-size: 11px; font-weight: bold;")
        self.dir_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        refresh_btn = QPushButton()
        refresh_btn.setIcon(load_icon("refresh.png"))
        refresh_btn.setToolTip("Refresh Tree")
        refresh_btn.setFixedSize(20, 20)
        refresh_btn.setStyleSheet("border: none;")
        refresh_btn.clicked.connect(self.refresh_tree)

        new_file_btn = QPushButton()
        new_file_btn.setIcon(load_icon("new_file.png"))
        new_file_btn.setToolTip("New File")
        new_file_btn.setFixedSize(20, 20)
        new_file_btn.setStyleSheet("border: none;")
        new_file_btn.clicked.connect(lambda: self.create_item(is_folder=False))

        new_folder_btn = QPushButton()
        new_folder_btn.setIcon(load_icon("new_folder.png"))
        new_folder_btn.setToolTip("New Folder")
        new_folder_btn.setFixedSize(20, 20)
        new_folder_btn.setStyleSheet("border: none;")
        new_folder_btn.clicked.connect(lambda: self.create_item(is_folder=True))

        self.filter_btn = QPushButton()
        self.filter_btn.setIcon(load_icon("filter.png"))
        self.filter_btn.setToolTip("Filter Files")
        self.filter_btn.setFixedSize(20, 20)
        self.filter_btn.setCheckable(True)
        self.filter_btn.setStyleSheet("border: none;")
        self.filter_btn.clicked.connect(self.toggle_filter)

        toolbar_layout.addWidget(self.dir_label)
        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addWidget(new_file_btn)
        toolbar_layout.addWidget(new_folder_btn)
        toolbar_layout.addWidget(self.filter_btn)
        main_layout.addWidget(toolbar)

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
        main_layout.addWidget(self.filter_combo)

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

        main_layout.addWidget(self.tree)
        self.setLayout(main_layout)

    def show_model_menu(self):
        menu = QMenu()

        if self.models.get("LM Studio"):
            menu.addSection("LM Studio Models")
            for model in self.models["LM Studio"]:
                action = QAction(model, self)
                action.triggered.connect(lambda checked, m=model: self.switch_model(m, "lmstudio"))
                menu.addAction(action)
            menu.addSeparator()

        if self.models.get("Ollama"):
            menu.addSection("Ollama Models")
            for model in self.models["Ollama"]:
                action = QAction(model, self)
                action.triggered.connect(lambda checked, m=model: self.switch_model(m, "ollama"))
                menu.addAction(action)
            menu.addSeparator()

        if self.models.get("API"):
            menu.addSection("API Models")
            for model in self.models["API"]:
                action = QAction(model, self)
                action.triggered.connect(lambda checked, m=model: self.switch_model(m, "api"))
                menu.addAction(action)

    def switch_model(self, model_name, backend):
        self.current_model_name = model_name
        self.current_backend = backend
        self.model_changed.emit(model_name, backend)

    def refresh_tree(self):
        root_index = self.model.index(self.root_path)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(root_index))

    def set_root_path(self, path: str):
        try:
            if not path:
                return
            self.root_path = path
            # update label text
            try:
                self.dir_label.setText(os.path.basename(self.root_path) or self.root_path)
            except Exception:
                pass
            # update QFileSystemModel root and refresh tree view
            try:
                self.model.setRootPath(self.root_path)
            except Exception:
                pass
            self.refresh_tree()
        except Exception:
            pass

    def toggle_filter(self):
        self.filter_mode = not self.filter_mode
        self.filter_combo.setVisible(self.filter_mode)

    def apply_filter(self):
        selected = self.filter_combo.currentText()
        extensions = []
        if "Python Files" in selected:
            extensions = [".py"]
        elif "Text Files" in selected:
            extensions = [".txt"]
        elif "JSON Files" in selected:
            extensions = [".json"]
        elif "Python + Text" in selected:
            extensions = [".py", ".txt"]
        elif "Config Files" in selected:
            extensions = [".json", ".yaml", ".yml"]
        self.proxy_model.setAllowedExtensions(extensions)

    def on_item_clicked(self, index: QModelIndex):
        source_index = self.proxy_model.mapToSource(index)
        if not self.model.isDir(source_index):
            file_path = self.model.filePath(source_index)
            self.file_selected.emit(file_path)

    def create_item(self, is_folder=False):
        if self.creating_item:
            return

        parent_index = self.tree.rootIndex()
        parent_path = self.model.filePath(self.proxy_model.mapToSource(parent_index))
        temp_name = "New Folder" if is_folder else "New File"
        temp_path = os.path.join(parent_path, temp_name)

        counter = 1
        while os.path.exists(temp_path):
            temp_path = os.path.join(parent_path, f"{temp_name} {counter}")
            counter += 1

        self.creating_item = QLineEdit(temp_name, self.tree)
        self.creating_item.setFrame(False)
        self.creating_item.setStyleSheet("background-color: #333; color: #fff; border: 1px solid #555;")
        self.creating_item.setFocus()
        self.creating_item.selectAll()
        self.creating_item.setGeometry(25, 25, 200, 22)
        self.creating_item.show()

        self.creating_item.returnPressed.connect(lambda: self.finalize_creation(parent_path, is_folder))
        self.creating_item.editingFinished.connect(self.cancel_creation)

    def finalize_creation(self, parent_path, is_folder):
        name = self.creating_item.text().strip()
        if not name:
            self.cancel_creation()
            return

        new_path = os.path.join(parent_path, name)
        try:
            if is_folder:
                os.makedirs(new_path, exist_ok=False)
            else:
                with open(new_path, "w") as f:
                    f.write("")
        except FileExistsError:
            pass

        self.creating_item.deleteLater()
        self.creating_item = None
        self.refresh_tree()

    def cancel_creation(self):
        if self.creating_item:
            self.creating_item.deleteLater()
            self.creating_item = None


class ExtensionFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.allowed_extensions = []

    def setAllowedExtensions(self, extensions):
        self.allowed_extensions = [ext.lower() for ext in extensions]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        file_path = self.sourceModel().filePath(index)
        if os.path.isdir(file_path):
            return True

        if not self.allowed_extensions:
            return True

        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.allowed_extensions
