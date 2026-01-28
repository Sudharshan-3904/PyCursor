from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QPushButton, 
                             QLabel, QHBoxLayout, QMessageBox, QWidget, QListWidgetItem,
                             QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

class CreateVenvThread(QThread):
    finished = pyqtSignal(str, str) # status, message
    
    def __init__(self, env_manager):
        super().__init__()
        self.env_manager = env_manager
        
    def run(self):
        try:
            path = self.env_manager.create_venv()
            self.finished.emit("success", path)
        except Exception as e:
            self.finished.emit("error", str(e))

class EnvironmentSelectionDialog(QDialog):
    env_selected = pyqtSignal(str, str) # name, path

    def __init__(self, parent=None, env_manager=None, current_env_path=None):
        super().__init__(parent)
        self.setWindowTitle("Select Python Interpreter")
        self.resize(600, 400)
        self.env_manager = env_manager
        self.current_env_path = current_env_path
        
        # Apply some basic styling if parent has stylesheet
        if parent:
            self.setStyleSheet(parent.styleSheet())
            
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Select an environment to use for code execution and tools:"))
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.refresh_envs()

        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Create New .venv")
        self.create_btn.clicked.connect(self.start_create_venv)
        btn_layout.addWidget(self.create_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.select_btn = QPushButton("Select Interpreter")
        self.select_btn.clicked.connect(self.select_env)
        self.select_btn.setDefault(True)
        btn_layout.addWidget(self.select_btn)
        
        self.layout.addLayout(btn_layout)
        
        # Progress for creation
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

    def refresh_envs(self):
        self.list_widget.clear()
        envs = self.env_manager.list_environments()
        for env in envs:
            display_text = f"{env['name']} - {env['path']}"
            if env['path'] == self.current_env_path:
                display_text += " (Current)"
                
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, env)
            
            self.list_widget.addItem(item)
            if env['path'] == self.current_env_path:
                self.list_widget.setCurrentItem(item)

    def select_env(self):
        item = self.list_widget.currentItem()
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            self.env_selected.emit(data['name'], data['path'])
            self.accept()

    def start_create_venv(self):
        self.create_btn.setEnabled(False)
        self.list_widget.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("Creating virtual environment... %p%")
        
        self.thread = CreateVenvThread(self.env_manager)
        self.thread.finished.connect(self.on_create_finished)
        self.thread.start()

    def on_create_finished(self, status, message):
        self.create_btn.setEnabled(True)
        self.list_widget.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if status == "success":
            QMessageBox.information(self, "Venv Created", f"Successfully created environment at:\n{message}")
            self.refresh_envs()
            # Auto-select the new one
            # Find the item with this path
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                data = item.data(Qt.ItemDataRole.UserRole)
                if data['path'] == message:
                    self.list_widget.setCurrentItem(item)
                    break
        else:
            QMessageBox.critical(self, "Creation Failed", f"Error creating venv: {message}")
