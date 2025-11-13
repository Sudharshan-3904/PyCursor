# main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QFileDialog, QMenuBar, QApplication
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from editor import CodeEditor
from sidebar import SideBar
from terminal import Terminal
from core.ai.ai_module import install_ai_actions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCursor IDE")
        self.resize(1200, 800)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.sidebar = SideBar(self)
        self.editor = CodeEditor()
        self.terminal = Terminal()

        main_splitter.addWidget(self.sidebar)
        main_splitter.addWidget(self.editor)
        main_splitter.setStretchFactor(1, 4)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        layout.addWidget(self.terminal)
        container.setLayout(layout)

        self.setCentralWidget(container)
        self._create_menu_bar()

        # Install AI actions and get the ai_manager back
        # install_ai_actions will add the menu action, shortcut, and wire everything up.
        # It will also attach an `ai_manager` and `llm_client` to this MainWindow object to allow dynamic control.
        self.ai_manager = install_ai_actions(self)  # returns the ai_manager instance

        # connect sidebar model change events to update LLM client config (so you can pick model/backend in sidebar)
        try:
            self.sidebar.model_changed.connect(self.on_model_changed)
        except Exception:
            # model_changed may not exist in all sidebar versions
            pass

    def _create_menu_bar(self):
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save File", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        self.setMenuBar(menu_bar)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.editor.setText(f.read())
            # store the current file path for the ai flow and status
            self.current_file_path = file_path
            self.statusBar().showMessage(f"Opened {file_path}", 3000)

    def save_file(self):
        # save to the known path if set, else ask
        if hasattr(self, "current_file_path") and self.current_file_path:
            file_path = self.current_file_path
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;All Files (*)")
            if not file_path:
                return
            self.current_file_path = file_path

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.editor.text())  # QsciScintilla uses .text()
        self.statusBar().showMessage(f"Saved {file_path}", 3000)

    def on_model_changed(self, model_name: str, backend: str):
        """
        Called when the sidebar model is changed. We forward the selected model/backend
        to the AI manager's llm client config so future requests use the chosen model.
        """
        # ai_manager and llm_client are attached by install_ai_actions
        try:
            llm_client = getattr(self, "_llm_client", None)
            if llm_client:
                # Simple, flexible contract: set config keys
                llm_client.config["model_name"] = model_name
                llm_client.config["backend"] = backend
                self.statusBar().showMessage(f"Switched model to {model_name} ({backend})", 3000)
        except Exception as e:
            print("Failed to switch AI model:", e)
