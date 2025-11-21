import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QTabWidget, QFileDialog,
    QMessageBox, QTabBar, QPushButton, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QStatusBar, QToolBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QAction, QIcon, QFont

from core.ui.sidebar import SideBar
from core.ui.editor import CodeEditor
from core.ui.terminal import Terminal
from core.ai.ai_engine import AIEngine
from core.utils import load_icon
from core.ui.theme import get_stylesheet, COLORS



class PyCursorMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCursor IDE")
        self.resize(1400, 900)
        
        self.setStyleSheet(get_stylesheet())

        self.settings_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "settings.json"
        )
        self._settings = self._load_settings()
        self.project_path = self._settings.get("last_open_folder", os.getcwd())

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.setDocumentMode(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.setCentralWidget(self.editor_tabs)

        self.sidebar = SideBar(root_path=self.project_path)
        self.sidebar.file_selected.connect(self.open_file_in_tab)

        self.sidebar_dock = QDockWidget("EXPLORER", self)
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)

        self.ai_widget = AIEngine()
        self.ai_widget.set_main_window(self)

        self.ai_dock = QDockWidget("AI ASSISTANT", self)
        self.ai_dock.setWidget(self.ai_widget)
        self.ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.ai_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)

        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.setTabsClosable(False)
        self.terminal_tabs.setMovable(True)
        self.add_terminal_tab("Terminal 1")

        self.terminal_dock = QDockWidget("TERMINAL", self)
        self.terminal_dock.setWidget(self.terminal_tabs)
        self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.terminal_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        self.create_activity_bar()

        self.create_status_bar()
        
        self.create_menu_bar()

    def create_activity_bar(self):
        """Create VS Code-style Activity Bar using QToolBar"""
        activity_bar = QToolBar("Activity Bar")
        activity_bar.setMovable(False)
        activity_bar.setFloatable(False)
        activity_bar.setOrientation(Qt.Orientation.Vertical)
        activity_bar.setIconSize(QSize(28, 28))
        activity_bar.setStyleSheet(f"""
            QToolBar {{
                background-color: {COLORS['bg_secondary']};
                border-right: 1px solid {COLORS['border']};
                spacing: 10px;
                padding: 10px 0px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-left: 2px solid transparent;
                padding: 8px;
                border-radius: 0px;
            }}
            QToolButton:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QToolButton:checked {{
                border-left: 2px solid {COLORS['accent_blue']};
                background-color: {COLORS['bg_tertiary']};
            }}
        """)
        
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, activity_bar)
        
        explorer_action = QAction(load_icon("folder.svg"), "Explorer", self)
        explorer_action.setCheckable(True)
        explorer_action.setChecked(True)
        explorer_action.triggered.connect(lambda: self.toggle_view("explorer"))
        activity_bar.addAction(explorer_action)
        self.explorer_action = explorer_action
        
        search_action = QAction(load_icon("search.svg"), "Search", self)
        search_action.setCheckable(True)
        search_action.triggered.connect(lambda: self.toggle_view("search"))
        activity_bar.addAction(search_action)
        self.search_action = search_action
        
        git_action = QAction(load_icon("git.svg"), "Source Control", self)
        git_action.setCheckable(True)
        git_action.triggered.connect(lambda: self.toggle_view("git"))
        activity_bar.addAction(git_action)
        self.git_action = git_action
        
        ai_action = QAction(load_icon("ai_chat.svg"), "AI Assistant", self)
        ai_action.setCheckable(True)
        ai_action.setChecked(True)
        ai_action.triggered.connect(lambda: self.toggle_view("ai"))
        activity_bar.addAction(ai_action)
        self.ai_action = ai_action

        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        activity_bar.addWidget(empty)

        settings_action = QAction(load_icon("settings.svg"), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        activity_bar.addAction(settings_action)

    def open_settings(self):
        from core.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self, api_handler=self.ai_widget.api_model_handler)
        dialog.exec()

    def toggle_view(self, view_name):
        """Handle Activity Bar clicks"""
        if view_name == "explorer":
            visible = self.sidebar_dock.isVisible()
            if visible and self.explorer_action.isChecked():
                pass
            
            self.sidebar_dock.setVisible(self.explorer_action.isChecked())
            
        elif view_name == "ai":
            self.ai_dock.setVisible(self.ai_action.isChecked())
            
        elif view_name in ["search", "git"]:
            pass
    
    def create_status_bar(self):
        """Create VS Code-style status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        self.status_file_label = QLabel("No file open")
        self.status_file_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_file_label)
        
        status_bar.addWidget(QLabel("|"))
        
        self.status_cursor_label = QLabel("Ln 1, Col 1")
        self.status_cursor_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_cursor_label)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        status_bar.addWidget(spacer)
        
        self.status_language_label = QLabel("Python")
        self.status_language_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_language_label)
        
        status_bar.addWidget(QLabel("|"))
        
        self.status_encoding_label = QLabel("UTF-8")
        self.status_encoding_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_encoding_label)
        
        status_bar.addWidget(QLabel("|"))
        
        self.status_git_label = QLabel("main")
        self.status_git_label.setStyleSheet(f"color: {COLORS['accent_blue']}; padding: 0 10px;")
        status_bar.addWidget(self.status_git_label)
        
        self.editor_tabs.currentChanged.connect(self.update_status_bar)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)

        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut("Ctrl+K Ctrl+O")
        open_folder_action.triggered.connect(self.open_folder_dialog)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(lambda: self.save_file(save_as=True))

        file_menu.addAction(open_action)
        file_menu.addAction(open_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        
        close_tab_action = QAction("&Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(lambda: self.close_editor_tab(self.editor_tabs.currentIndex()))
        file_menu.addAction(close_tab_action)

        edit_menu = menu_bar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find", self)
        find_action.setShortcut("Ctrl+F")
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace", self)
        replace_action.setShortcut("Ctrl+H")
        edit_menu.addAction(replace_action)

        view_menu = menu_bar.addMenu("&View")
        
        toggle_sidebar_action = QAction("Toggle &Explorer", self)
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.triggered.connect(lambda: self.sidebar_dock.setVisible(not self.sidebar_dock.isVisible()))
        view_menu.addAction(toggle_sidebar_action)
        
        toggle_terminal_action = QAction("Toggle &Terminal", self)
        toggle_terminal_action.setShortcut("Ctrl+`")
        toggle_terminal_action.triggered.connect(lambda: self.terminal_dock.setVisible(not self.terminal_dock.isVisible()))
        view_menu.addAction(toggle_terminal_action)
        
        toggle_ai_action = QAction("Toggle &AI Assistant", self)
        toggle_ai_action.setShortcut("Ctrl+Shift+A")
        toggle_ai_action.triggered.connect(lambda: self.ai_dock.setVisible(not self.ai_dock.isVisible()))
        view_menu.addAction(toggle_ai_action)

        run_menu = menu_bar.addMenu("&Run")
        run_action = QAction("&Run Code", self)
        run_action.setShortcut("Ctrl+Shift+R")
        run_action.triggered.connect(self.execute_current_file)
        run_menu.addAction(run_action)
    
    def update_status_bar(self):
        """Update status bar with current file info"""
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'file_path'):
            filename = os.path.basename(editor.file_path)
            self.status_file_label.setText(filename)
            
            ext = os.path.splitext(filename)[1].lower()
            lang_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.html': 'HTML',
                '.css': 'CSS',
                '.json': 'JSON',
                '.md': 'Markdown',
                '.txt': 'Plain Text'
            }
            self.status_language_label.setText(lang_map.get(ext, 'Unknown'))
        else:
            self.status_file_label.setText("No file open")
            self.status_language_label.setText("—")

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
