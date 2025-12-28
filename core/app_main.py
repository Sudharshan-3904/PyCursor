"""
Main Application Module for PyCursor IDE.

This module is the entry point for the PyCursor IDE application. It defines the main window
(`PyCursorMain`) and orchestrates the initialization of various components such as the
editor, sidebar, terminal, AI assistant, and Git integration. It also handles the
startup process including model detection and Git repository checking in a background thread.
"""
import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QTabWidget, QFileDialog,
    QMessageBox, QTabBar, QPushButton, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QStatusBar, QToolBar, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont

from core.ui.sidebar import SideBar
from core.ui.editor import CodeEditor
from core.ui.terminal import Terminal
from core.ai.ai_engine import AIEngine
from core.utilities.utils import load_icon
from core.ui.theme import get_stylesheet, COLORS
from core.utilities.keybindings import KeyBindingsManager
from core.git.git_panel import GitPanel
from core.git.git_handler import GitHandler
from core.ai.local_model_handler import LocalModelHandler
from core.ui.keybindings_dialog import KeybindingsDialog
from core.ui.log_panel import LogPanel
from core.ide.editor_manager import EditorManager
from core.ui.menu_manager import MenuManager
from core.ui.extensions_panel import ExtensionsPanel
from core.ui.search_panel import SearchPanel


class StartupThread(QThread):
    models_ready = pyqtSignal(dict)
    git_ready = pyqtSignal(bool, object, object, object)

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

    def run(self):
        try:
            handler = LocalModelHandler()
            models = handler.detect_models()
            self.models_ready.emit(models)
        except Exception as e:
            print(f"Model detection failed: {e}")
            self.models_ready.emit({})

        try:
            if self.project_path:
                git = GitHandler(self.project_path)
                if git.is_repository(self.project_path):
                    git.open_repository(self.project_path)
                    current_branch = git.get_current_branch()
                    branches = git.get_branches()
                    status = git.get_status()
                    self.git_ready.emit(True, status, branches, current_branch)
                else:
                    self.git_ready.emit(False, None, None, None)
        except Exception as e:
            print(f"Git check failed: {e}")
            self.git_ready.emit(False, None, None, None)


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
        self.setCentralWidget(self.editor_tabs)
        self.editor_manager = EditorManager(self, self.editor_tabs)

        self.sidebar_stack = QStackedWidget()

        self.sidebar = SideBar(root_path=self.project_path)
        self.sidebar.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.sidebar)

        # 2. Git Panel
        self.git_panel = GitPanel(repo_path=self.project_path)
        self.git_panel.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.git_panel)

        # 3. Logs Panel
        self.log_panel = LogPanel()
        self.sidebar_stack.addWidget(self.log_panel)

        # 4. Extensions Panel
        self.extensions_panel = ExtensionsPanel(self)
        self.sidebar_stack.addWidget(self.extensions_panel)

        # 5. Search Panel
        self.search_panel = SearchPanel(root_path=self.project_path)
        self.search_panel.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.search_panel)

        self.sidebar_dock = QDockWidget("EXPLORER", self)
        self.sidebar_dock.setWidget(self.sidebar_stack)
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
        
        self.keybindings = KeyBindingsManager()
        self.setup_keybindings()
        
        
        self.create_menu_bar()

        # Start background loading
        self.startup_thread = StartupThread(self.project_path)
        self.startup_thread.models_ready.connect(self.on_models_loaded)
        self.startup_thread.git_ready.connect(self.on_git_ready)
        self.startup_thread.start()

    def on_models_loaded(self, models):
        if hasattr(self, 'ai_widget'):
            self.ai_widget.update_models(models)
            model_count = len(models)
            if hasattr(self, 'log_panel'):
                self.log_panel.log(f"[Startup] Detected {model_count} AI models.")
                for name in models:
                    self.log_panel.log(f"  - {name}")

    def on_git_ready(self, is_repo, status, branches, current_branch):
        if hasattr(self, 'git_panel'):
            if is_repo:
                self.log_panel.log(f"[Startup] Git repository active: {current_branch}")
                self.git_panel.stack.setCurrentWidget(self.git_panel.repo_widget)
                self.git_panel.refresh(status, branches, current_branch)
                if current_branch:
                    self.status_git_label.setText(current_branch)
            else:
                self.log_panel.log("[Startup] No Git repository detected.")
                self.git_panel.stack.setCurrentWidget(self.git_panel.no_repo_widget)
                self.status_git_label.setText("")


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

        extensions_action = QAction(load_icon("extensions.svg"), "Extensions", self) # Use puzzle icon if extensions.svg missing
        extensions_action.setCheckable(True)
        extensions_action.triggered.connect(lambda: self.toggle_view("extensions"))
        activity_bar.addAction(extensions_action)
        self.extensions_action = extensions_action
        
        logs_action = QAction(load_icon("output.svg"), "App Logs", self) # Assuming output.svg exists or uses fallback
        logs_action.setCheckable(True)
        logs_action.triggered.connect(lambda: self.toggle_view("logs"))
        activity_bar.addAction(logs_action)
        self.logs_action = logs_action


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
        """Handle Activity Bar clicks with radio button behavior"""
        sidebar_actions = {
            "explorer": self.explorer_action,
            "search": self.search_action,
            "git": self.git_action,
            "logs": self.logs_action,
            "extensions": self.extensions_action,
        }
        
        if view_name in sidebar_actions:
            current_action = sidebar_actions[view_name]
            
            if current_action.isChecked():
                was_active = False
                if self.sidebar_dock.isVisible():
                    # Check current stack index
                    current_index = self.sidebar_stack.currentIndex()
                    if view_name == "explorer" and current_index == 0:
                        was_active = True
                    elif view_name == "git" and current_index == 1:
                        was_active = True
                    # Search would be index 2
                
                if was_active:
                    self.sidebar_dock.setVisible(False)
                    current_action.setChecked(False)
                    current_action.setProperty("was_active", False)
                else:
                    for name, action in sidebar_actions.items():
                        if name != view_name:
                            action.setChecked(False)
                            action.setProperty("was_active", False)
                    
                    current_action.setProperty("was_active", True)
                    self.sidebar_dock.setVisible(True)
                    
                    if view_name == "explorer":
                        self.sidebar_stack.setCurrentIndex(0)
                        self.sidebar_dock.setWindowTitle("EXPLORER")
                    elif view_name == "git":
                        self.sidebar_stack.setCurrentIndex(1)
                        self.sidebar_dock.setWindowTitle("SOURCE CONTROL")
                        self.git_panel.refresh()
                    elif view_name == "logs":
                        self.sidebar_stack.setCurrentIndex(2)
                        self.sidebar_dock.setWindowTitle("APP LOGS")
                    elif view_name == "extensions":
                        self.sidebar_stack.setCurrentIndex(3)
                        self.sidebar_dock.setWindowTitle("EXTENSIONS")
                    elif view_name == "search":
                        self.sidebar_stack.setCurrentIndex(4)
                        self.sidebar_dock.setWindowTitle("SEARCH")
                        if self.project_path:
                            self.search_panel.set_project_path(self.project_path)
            else:
                self.sidebar_dock.setVisible(False)
                current_action.setProperty("was_active", False)
    
    
    def create_status_bar(self):
        """Create VS Code-style status bar"""
        status_bar = QStatusBar()
        status_bar.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; color: {COLORS['text_primary']};")
        self.setStatusBar(status_bar)
        
        # Left side
        self.status_git_label = QLabel("")
        self.status_git_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px; font-weight: bold;")
        status_bar.addWidget(self.status_git_label)
        
        self.status_file_label = QLabel("No file open")
        self.status_file_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_file_label)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        status_bar.addWidget(spacer)
        
        # Right side
        self.status_cursor_label = QLabel("Ln 1, Col 1")
        self.status_cursor_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_cursor_label)
        
        self.status_encoding_label = QLabel("UTF-8")
        self.status_encoding_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_encoding_label)
        
        self.status_language_label = QLabel("Plain Text")
        self.status_language_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 0 10px;")
        status_bar.addWidget(self.status_language_label)
        
        # Connect tab changes via manager is handled inside manager, but manager calls update_status_bar
        # self.editor_tabs.currentChanged.connect(self.update_status_bar)


    def create_menu_bar(self):
        self.menu_manager = MenuManager(self)
        self.menu_manager.setup_menu_bar()
        return

    
    
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
            self.status_language_label.setText(lang_map.get(ext, 'Plain Text'))
            
            # Update cursor position immediately
            line, col = editor.getCursorPosition()
            self.update_cursor_position(line, col)
        else:
            self.status_file_label.setText("No file open")
            self.status_language_label.setText("—")
            self.status_cursor_label.setText("Ln 1, Col 1")

    def update_cursor_position(self, line, col):
        """Update cursor position label"""
        self.status_cursor_label.setText(f"Ln {line + 1}, Col {col + 1}")

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


        self.editor_manager.close_all_tabs()
        self.project_path = folder
        self._update_last_open_folder(folder)

        if hasattr(self.sidebar, "setRootPath"):
            self.sidebar.setRootPath(folder)
        elif hasattr(self.sidebar, "set_root_path"):
            self.sidebar.set_root_path(folder)
        elif hasattr(self.sidebar, "refresh"):
            self.sidebar.refresh()
            
        # Update Git Panel
        if hasattr(self, 'git_panel'):
            self.git_panel.set_repository(folder)

        for i in range(self.terminal_tabs.count()):
            term = self.terminal_tabs.widget(i)
            if hasattr(term, "set_project_path"):
                term.set_project_path(folder)

    # Delegated methods for potential external calls (like from Sidebar)
    def open_file_in_tab(self, file_path: str, line_number: int = None):
        self.editor_manager.open_file(file_path)
        if line_number is not None:
             editor = self.get_current_editor()
             if editor:
                 cursor = editor.textCursor()
                 cursor.movePosition(cursor.MoveOperation.Start)
                 cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_number - 1)
                 editor.setTextCursor(cursor)
                 editor.centerCursor()
                 editor.setFocus()

    def save_file(self):
        self.editor_manager.save_current_file()

    def get_current_editor(self):
        return self.editor_manager.get_current_editor()
            
    def close_editor_tab(self, index):
        self.editor_manager.close_tab(index)

    def save_all_files(self):
        self.editor_manager.save_all_files()
    
    def close_all_editor_tabs(self):
        self.editor_manager.close_all_tabs()





    
    def exit_application(self):
        """Close the application"""
        self.close()

    def show_about(self):
        QMessageBox.about(
            self,
            "About PyCursor",
            "<h3>PyCursor IDE</h3>"
            "<p>A modern, AI-powered Python IDE.</p>"
            "<p>Version: 0.2.0 (Dev)</p>"
        )





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

    def setup_keybindings(self):
        """Register all keyboard shortcuts using the keybindings manager"""
        self.keybindings.register_shortcut("file.open", self.open_file_dialog, self)
        self.keybindings.register_shortcut("file.open_folder", self.open_folder_dialog, self)
        self.keybindings.register_shortcut("file.save", self.save_file, self)
        self.keybindings.register_shortcut("file.save_as", lambda: self.save_file(save_as=True), self)
        self.keybindings.register_shortcut("file.close_tab", 
            lambda: self.close_editor_tab(self.editor_tabs.currentIndex()), self)
        
        self.keybindings.register_shortcut("view.toggle_explorer", 
            lambda: self.sidebar_dock.setVisible(not self.sidebar_dock.isVisible()), self)
        self.keybindings.register_shortcut("view.toggle_terminal", 
            lambda: self.terminal_dock.setVisible(not self.terminal_dock.isVisible()), self)
        self.keybindings.register_shortcut("view.toggle_ai", 
            lambda: self.ai_dock.setVisible(not self.ai_dock.isVisible()), self)
        
        self.keybindings.register_shortcut("run.run_code", self.execute_current_file, self)
        
        self.keybindings.register_shortcut("navigation.next_tab", self.next_tab, self)
        self.keybindings.register_shortcut("navigation.previous_tab", self.previous_tab, self)
        
        self.keybindings.register_shortcut("app.quick_open", self.show_quick_open, self)
        self.keybindings.register_shortcut("app.command_palette", self.show_command_palette, self)
        self.keybindings.register_shortcut("app.settings", self.open_settings, self)

    def next_tab(self):
        """Switch to the next editor tab"""
        current = self.editor_tabs.currentIndex()
        count = self.editor_tabs.count()
        if count > 0:
            self.editor_tabs.setCurrentIndex((current + 1) % count)

    def previous_tab(self):
        """Switch to the previous editor tab"""
        current = self.editor_tabs.currentIndex()
        count = self.editor_tabs.count()
        if count > 0:
            self.editor_tabs.setCurrentIndex((current - 1) % count)

    def show_quick_open(self):
        """Show quick open file dialog"""
        from core.ui.command_palette import CommandPalette
        palette = CommandPalette(self, mode="files", project_path=self.project_path)
        
        parent_geometry = self.geometry()
        palette_geometry = palette.geometry()
        x = parent_geometry.x() + (parent_geometry.width() - palette_geometry.width()) // 2
        y = parent_geometry.y() + parent_geometry.height() // 4
        palette.move(x, y)
        
        palette.exec()

    def show_command_palette(self):
        """Show command palette"""
        from core.ui.command_palette import CommandPalette
        
        commands = [
            ("Open File", self.open_file_dialog),
            ("Open Folder", self.open_folder_dialog),
            ("Save File", self.save_file),
            ("Close Tab", lambda: self.close_editor_tab(self.editor_tabs.currentIndex())),
            ("Toggle Explorer", lambda: self.sidebar_dock.setVisible(not self.sidebar_dock.isVisible())),
            ("Toggle Terminal", lambda: self.terminal_dock.setVisible(not self.terminal_dock.isVisible())),
            ("Toggle AI Assistant", lambda: self.ai_dock.setVisible(not self.ai_dock.isVisible())),
            ("Run File", self.execute_current_file),
            ("Settings", self.open_settings),
        ]
        
        palette = CommandPalette(self, mode="commands", actions=commands)
        
        parent_geometry = self.geometry()
        palette_geometry = palette.geometry()
        x = parent_geometry.x() + (parent_geometry.width() - palette_geometry.width()) // 2
        y = parent_geometry.y() + parent_geometry.height() // 4
        palette.move(x, y)
        
        palette.exec()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
