import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QTabWidget, QFileDialog,
    QMessageBox, QTabBar, QPushButton, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from core.ui.sidebar import SideBar
from core.ui.editor import CodeEditor
from core.ui.terminal import Terminal
from core.ai.ai_engine import AIEngine
from core.utils import load_icon



class PyCursorMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCursor IDE")
        self.resize(1200, 800)

        self.settings_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "settings.json"
        )
        self._settings = self._load_settings()
        self.project_path = self._settings.get("last_open_folder", os.getcwd())

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.setCentralWidget(self.editor_tabs)

        self.sidebar = SideBar()
        self.sidebar.file_selected.connect(self.open_file_in_tab)

        self.sidebar_dock = QDockWidget("Explorer", self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)

        self.ai_widget = AIEngine()
        self.ai_widget.set_main_window(self)

        self.ai_dock = QDockWidget("AI Assistant", self)
        self.ai_dock.setWidget(self.ai_widget)
        self.ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)

        self.status_dock = QDockWidget("Status", self)
        status_widget = QWidget()
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(6, 6, 6, 6)
        self.right_status_label = QLabel("Ready")
        status_layout.addWidget(self.right_status_label)
        status_layout.addStretch()
        status_widget.setLayout(status_layout)
        self.status_dock.setWidget(status_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.status_dock)

        self.terminal_tabs = QTabWidget()
        self.add_terminal_tab("Terminal 1")

        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setWidget(self.terminal_tabs)
        self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file_dialog)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.open_folder_dialog)

        save_action = QAction("Save File", self)
        save_action.triggered.connect(self.save_file)

        file_menu.addAction(open_action)
        file_menu.addAction(open_folder_action)
        file_menu.addAction(save_action)

        run_menu = menu_bar.addMenu("Run")
        run_action = QAction("Run Code", self)
        run_action.setShortcut("Ctrl+Shift+R")
        run_action.triggered.connect(self.execute_current_file)
        run_menu.addAction(run_action)

    def open_file_dialog(self):
        start_dir = self.project_path or os.getcwd()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", start_dir)
        if file_path:
            self.open_file_in_tab(file_path)
            self._update_last_open_folder(os.path.dirname(file_path))

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder", self.project_path)
        if not folder:
            return

        self.close_all_editor_tabs()
        self.project_path = folder
        self._update_last_open_folder(folder)

        if hasattr(self.sidebar, "setRootPath"):
            self.sidebar.setRootPath(folder)
        elif hasattr(self.sidebar, "set_root_path"):
            self.sidebar.set_root_path(folder)
        elif hasattr(self.sidebar, "refresh"):
            self.sidebar.refresh()

        for i in range(self.terminal_tabs.count()):
            term = self.terminal_tabs.widget(i)
            if hasattr(term, "set_project_path"):
                term.set_project_path(folder)

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        file_path = getattr(editor, "file_path", None)

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(editor.text())
            editor.setModified(False)
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", self.project_path)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(editor.text())
            editor.file_path = file_path
            editor.setModified(False)

            idx = self.editor_tabs.currentIndex()
            self.editor_tabs.setTabText(idx, os.path.basename(file_path))

            self._update_last_open_folder(os.path.dirname(file_path))

    def open_file_in_tab(self, file_path: str):
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if getattr(editor, "file_path", None) == file_path:
                self.editor_tabs.setCurrentIndex(i)
                return

        editor = CodeEditor()
        editor.file_path = file_path

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                editor.setText(f.read())
        except Exception as e:
            print(f"Failed to open {file_path}: {e}")
            return

        idx = self.editor_tabs.addTab(editor, os.path.basename(file_path))
        self.editor_tabs.setCurrentIndex(idx)

        close_btn = QPushButton()
        close_btn.setIcon(load_icon("close.png", size=12))
        close_btn.setFixedSize(18, 18)
        close_btn.setStyleSheet("border: none; padding: 0; margin-left: 4px;")
        close_btn.clicked.connect(lambda _, i=idx: self.close_editor_tab(i))

        tabbar = self.editor_tabs.tabBar()
        tabbar.setTabButton(idx, QTabBar.ButtonPosition.RightSide, close_btn)

    def close_editor_tab(self, index):
        editor = self.editor_tabs.widget(index)
        if not editor:
            self.editor_tabs.removeTab(index)
            return

        modified = False
        if hasattr(editor, "isModified") and callable(editor.isModified):
            modified = editor.isModified()

        if modified:
            filename = os.path.basename(getattr(editor, "file_path", "Untitled"))
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to {filename}?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_file()

        self.editor_tabs.removeTab(index)
        editor.deleteLater()

    def get_current_editor(self):
        editor = self.editor_tabs.currentWidget()
        if isinstance(editor, CodeEditor):
            return editor
        return None

    def notify_lines_added(self, filename: str, added_lines: int):
        self.right_status_label.setText(f"{added_lines} lines added to {filename}")
        QTimer.singleShot(4000, lambda: self.right_status_label.setText("Ready"))

    def execute_current_file(self):
        editor = self.get_current_editor()
        if not editor:
            QMessageBox.warning(self, "No File Open", "Open a Python file first.")
            return

        file_path = getattr(editor, "file_path", None)

        if not file_path:
            import tempfile
            fd, file_path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, "w") as f:
                f.write(editor.text())
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(editor.text())

        terminal = self.terminal_tabs.currentWidget()
        if terminal and hasattr(terminal, "execute_command"):
            terminal.execute_command(f"python \"{file_path}\"")

    def add_terminal_tab(self, name="Terminal"):
        term = Terminal(project_path=self.project_path)
        self.terminal_tabs.addTab(term, name)

    def _load_settings(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except Exception:
            pass

    def _update_last_open_folder(self, folder):
        if folder:
            self.project_path = folder
            self._settings["last_open_folder"] = folder
            self._save_settings()

    def close_all_editor_tabs(self):
        for i in range(self.editor_tabs.count() - 1, -1, -1):
            self.close_editor_tab(i)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
