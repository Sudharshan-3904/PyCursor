import sys
import os
import json
import subprocess
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTabWidget, QFileDialog, QMessageBox, QTabBar, QPushButton, QWidget, QLabel, QVBoxLayout
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
        self.close_icon = load_icon("close.png")
        self.settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")
        self._settings = self._load_settings()
        self.project_path = self._settings.get("last_open_folder", os.getcwd())

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.setCentralWidget(self.editor_tabs)
        self.editor_tabs.setStyleSheet("""
            QTabBar::close-button {
                image: url(close.png);
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {se
                image: url(close-icon-hover.png);
            }
        """)

        self.sidebar = SideBar()
        self.sidebar.file_selected.connect(self.open_file_in_tab)

        self.sidebar_dock = QDockWidget("Explorer", self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)

        self.ai_widget = AIEngine()
        try:
            self.ai_widget.set_main_window(self)
        except Exception:
            pass
        self.ai_dock = QDockWidget("AI Assistant", self)
        self.ai_dock.setWidget(self.ai_widget)
        self.ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.ai_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
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
        self.status_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.status_dock)

        self.terminal_tabs = QTabWidget()
        self.add_terminal_tab("Terminal 1")

        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setWidget(self.terminal_tabs)
        self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.terminal_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", start_dir, "All Files (*.*)")
        if file_path:
            self.open_file_in_tab(file_path)
            self._update_last_open_folder(os.path.dirname(file_path))

    def open_folder_dialog(self):
        start_dir = self.project_path or os.getcwd()
        folder = QFileDialog.getExistingDirectory(self, "Open Folder", start_dir)
        if folder:
            self._update_last_open_folder(folder)
            self.project_path = folder
            try:
                if hasattr(self.sidebar, "setRootPath"):
                    self.sidebar.setRootPath(folder)
                elif hasattr(self.sidebar, "set_root_path"):
                    self.sidebar.set_root_path(folder)
                elif hasattr(self.sidebar, "set_root"):
                    self.sidebar.set_root(folder)
                elif hasattr(self.sidebar, "refresh"):
                    self.sidebar.refresh()
            except Exception:
                pass

    def save_file(self):
        editor = self.editor_tabs.currentWidget()
        if editor:
            file_path = getattr(editor, "file_path", None)
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(editor.toPlainText())
                except Exception as e:
                    print(f"Failed to save {file_path}: {e}")
            else:
                start_dir = self.project_path or os.getcwd()
                file_path, _ = QFileDialog.getSaveFileName(self, "Save File", start_dir, "All Files (*.*)")
                if file_path:
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(editor.toPlainText())
                        editor.file_path = file_path
                        self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), os.path.basename(file_path))
                        self._update_last_open_folder(os.path.dirname(file_path))
                    except Exception as e:
                        print(f"Failed to save {file_path}: {e}")

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

        filename = os.path.basename(file_path)
        index = self.editor_tabs.addTab(editor, filename)
        self.editor_tabs.setCurrentWidget(editor)

        close_btn = QPushButton()
        close_btn.setIcon(load_icon("close.png", size=12))
        close_btn.setFixedSize(18, 18)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                margin-left: 4px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 80);
                border-radius: 3px;
            }
        """)
        close_btn.clicked.connect(lambda _, i=index: self.close_editor_tab(i))

        tab_bar = self.editor_tabs.tabBar()
        tab_bar.setTabButton(index, QTabBar.ButtonPosition.RightSide, close_btn)
        try:
            self._update_last_open_folder(os.path.dirname(file_path))
        except Exception:
            pass

    def _load_settings(self) -> dict:
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_settings(self):
        try:
            config_dir = os.path.dirname(self.settings_path)
            os.makedirs(config_dir, exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except Exception:
            pass

    def _update_last_open_folder(self, folder_path: str):
        if not folder_path:
            return
        self.project_path = folder_path
        self._settings["last_open_folder"] = folder_path
        self._save_settings()

    def close_editor_tab(self, index):
        editor = self.editor_tabs.widget(index)
        if hasattr(editor, "document") and editor.document().isModified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to {os.path.basename(editor.file_path)} before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_file()
        self.editor_tabs.removeTab(index)
        editor.deleteLater()

    def get_current_editor(self):
        try:
            return self.editor_tabs.currentWidget()
        except Exception:
            return None

    def notify_lines_added(self, filename: str, added_lines: int):
        try:
            self.right_status_label.setText(f"{added_lines} lines added to {filename}")
            QTimer.singleShot(4000, lambda: self.right_status_label.setText("Ready"))
        except Exception:
            pass

    def execute_current_file(self):
        editor = self.get_current_editor()
        if editor is None:
            QMessageBox.warning(self, "No File Open", "Please open a file to execute.")
            return

        file_path = getattr(editor, "file_path", None)
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(editor.text())
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save file: {e}")
                return
        else:
            import tempfile
            try:
                fd, file_path = tempfile.mkstemp(suffix=".py", text=True)
                with os.fdopen(fd, 'w', encoding="utf-8") as f:
                    f.write(editor.text())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create temporary file: {e}")
                return

        if self.terminal_tabs.count() == 0:
            self.add_terminal_tab()
        
        current_terminal_index = self.terminal_tabs.currentIndex()
        if current_terminal_index < 0:
            current_terminal_index = 0
        
        terminal = self.terminal_tabs.widget(current_terminal_index)
        
        if terminal and hasattr(terminal, 'execute_command'):
            command = f"python \"{file_path}\""
            terminal.execute_command(command)
        else:
            QMessageBox.information(self, "Executing", f"Running: python \"{file_path}\"")

    def add_terminal_tab(self, name="Terminal"):
        term = Terminal()
        self.terminal_tabs.addTab(term, name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
