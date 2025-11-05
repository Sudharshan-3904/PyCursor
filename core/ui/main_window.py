from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QTextEdit, QFileDialog, QMenuBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from .editor import CodeEditor
from .sidebar import SideBar
from .terminal import Terminal
from ..ai.ai_engine import AIEngine

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

        self.ai_engine = AIEngine()         # TODO - Implement the logic for the AI Engine

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

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
