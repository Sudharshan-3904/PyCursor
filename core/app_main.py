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
from core.ui.theme import get_stylesheet, THEMES
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
from core.env.env_manager import EnvironmentManager
from core.env.dependency_manager import DependencyManager
from core.ui.env_dialogs import EnvironmentSelectionDialog
from core.plugins.plugin_manager import PluginManager
from core.lsp.lsp_client import LSPManager

class StartupThread(QThread):
    """
    Background thread to perform initial system checks:
    1. Detect available AI models (Local/API).
    2. Check for Git repository status in the current project.
    """
    models_ready = pyqtSignal(dict)
    git_ready = pyqtSignal(bool, object, object, object)

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

    def run(self):
        """
        Executes model discovery and Git status checks.
        """
        try:
            handler = LocalModelHandler()
            models = handler.detect_models()
            self.models_ready.emit(models)
        except Exception as e:
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
            
            # Trigger RAG Indexing
            from core.ai.context_manager import ContextManager
            cm = ContextManager(self.project_path)
            if cm.rag_manager:
                cm.rag_manager.index_project()
        except Exception:
            self.git_ready.emit(False, None, None, None)

class PyCursorMain(QMainWindow):
    """
    Main Application Window for the PyCursor IDE.
    Coordinates all major components: Editors, Sidebar, Terminal, and AI Engine.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCursor IDE")
        self.resize(1400, 900)
        
        # Set Window Icon
        self.setWindowIcon(load_icon("darModeLogo.png"))
        
        # Configuration setup
        self.settings_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "settings.json"
        )
        self._settings = self._load_settings()
        self.apply_theme(self._settings.get("theme", "dark"))
        self.project_path = self._settings.get("last_open_folder", os.getcwd())

        # Central widget: Tabbed Editor Area
        self.editor_tabs = QTabWidget()
        self.setCentralWidget(self.editor_tabs)
        self.editor_manager = EditorManager(self, self.editor_tabs)

        # Primary Sidebar Navigation
        self.sidebar_stack = QStackedWidget()

        # Explorer Panel
        self.sidebar = SideBar(root_path=self.project_path)
        self.sidebar.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.sidebar)

        # Git Panel
        self.git_panel = GitPanel(repo_path=self.project_path)
        self.git_panel.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.git_panel)

        # App Logs Panel
        self.log_panel = LogPanel()
        self.sidebar_stack.addWidget(self.log_panel)

        # Extensions Panel
        self.extensions_panel = ExtensionsPanel(self)
        self.sidebar_stack.addWidget(self.extensions_panel)

        # Global Search Panel
        self.search_panel = SearchPanel(root_path=self.project_path)
        self.search_panel.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.search_panel)

        # Debug Panel
        from core.ui.debug_panel import DebugPanel
        self.debug_panel = DebugPanel()
        self.sidebar_stack.addWidget(self.debug_panel)

        # Sidebar Dock
        self.sidebar_dock = QDockWidget("EXPLORER", self)
        self.sidebar_dock.setWidget(self.sidebar_stack)
        self.sidebar_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)

        # AI Assistant Integration
        self.ai_widget = AIEngine()
        self.ai_widget.set_main_window(self)

        self.ai_dock = QDockWidget("AI ASSISTANT", self)
        self.ai_dock.setWidget(self.ai_widget)
        self.ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.ai_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)

        # Integrated Terminal
        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.setTabsClosable(False)
        self.terminal_tabs.setMovable(True)
        self.add_terminal_tab("Terminal 1")

        self.terminal_dock = QDockWidget("TERMINAL", self)
        self.terminal_dock.setWidget(self.terminal_tabs)
        self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.terminal_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        # Initialize core managers
        self.create_activity_bar()
        self.env_manager = EnvironmentManager(self.project_path)
        self.dep_manager = DependencyManager(self.project_path)
        
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.load_all_plugins()

        self.lsp_manager = LSPManager(self)
        self.lsp_manager.start()
        
        self.create_status_bar()
        self.update_env_status()
        
        self.keybindings = KeyBindingsManager()
        self.setup_keybindings()
        self.create_menu_bar()

        # Start background startup checks
        self.startup_thread = StartupThread(self.project_path)
        self.startup_thread.models_ready.connect(self.on_models_loaded)
        self.startup_thread.git_ready.connect(self.on_git_ready)
        self.startup_thread.start()

    def apply_theme(self, theme_name):
        """
        Updates the application stylesheet, icons, and refreshes all open editor instances.
        Debounced to prevent redundant refreshes when rapid changes occur.
        """
        if not hasattr(self, '_theme_timer'):
            self._theme_timer = QTimer(self)
            self._theme_timer.setSingleShot(True)
            self._theme_timer.timeout.connect(self._do_apply_theme)
        
        self._pending_theme = theme_name
        self._theme_timer.start(150) # 150ms debounce

    def _do_apply_theme(self):
        """
        Internal implementation of theme application.
        """
        theme_name = getattr(self, '_pending_theme', 'dark')
        print(f"[Theme] Applying theme: {theme_name}")
        from core.ui.theme import get_stylesheet
        self.setStyleSheet(get_stylesheet(theme=theme_name))
        self.refresh_icons(theme_name)
        
        if hasattr(self, 'editor_manager'):
             for i in range(self.editor_tabs.count()):
                 editor = self.editor_tabs.widget(i)
                 if hasattr(editor, 'refresh_theme'):
                     editor.refresh_theme(theme_name)
        
        if hasattr(self, 'sidebar'):
            if hasattr(self.sidebar, 'refresh_icons'): self.sidebar.refresh_icons(theme_name)
        
        if hasattr(self, 'ai_widget'):
            if hasattr(self.ai_widget, 'refresh_icons'): self.ai_widget.refresh_icons(theme_name)

        if hasattr(self, '_settings'):
            self._settings["theme"] = theme_name
            self._save_settings()

        QTimer.singleShot(500, self.show_welcome_screen)

    def refresh_icons(self, theme_name):
        """
        Updates all top-level activity bar and UI icons to match theme palette.
        """
        from core.ui.theme import get_icon_color
        color = get_icon_color(theme_name)
        
        if hasattr(self, 'explorer_action'): self.explorer_action.setIcon(load_icon("folder.svg", color=color))
        if hasattr(self, 'search_action'): self.search_action.setIcon(load_icon("search.svg", color=color))
        if hasattr(self, 'git_action'): self.git_action.setIcon(load_icon("git.svg", color=color))
        if hasattr(self, 'extensions_action'): self.extensions_action.setIcon(load_icon("extensions.svg", color=color))
        if hasattr(self, 'debug_action'): self.debug_action.setIcon(load_icon("debug.svg", color=color))
        if hasattr(self, 'logs_action'): self.logs_action.setIcon(load_icon("output.svg", color=color))

    def show_welcome_screen(self, force=False):
        """
        Displays the onboarding sequence if first run or forced via help menu.
        """
        if force or not self._settings.get("has_shown_welcome", False):
            from core.ui.welcome_dialog import WelcomeDialog
            dialog = WelcomeDialog(self)
            if dialog.exec() and not force:
                self._settings["has_shown_welcome"] = True
                self._save_settings()

    def show_go_to_line(self):
        """
        Opens a numeric input dialog to navigate to a specific line in the current editor.
        """
        editor = self.editor_manager.get_current_editor()
        if not editor: return
        
        from PyQt6.QtWidgets import QInputDialog
        line, ok = QInputDialog.getInt(self, "Go to Line", "Line number:", value=1, min=1)
        if ok:
            editor.setCursorPosition(line - 1, 0)
            editor.ensureLineVisible(line - 1)
            editor.setFocus()

    def on_models_loaded(self, models):
        """
        Callback for background model detection. Updates AI engine with discovered backends.
        """
        if hasattr(self, 'ai_widget'):
            self.ai_widget.update_models(models)

    def on_git_ready(self, is_repo, status, branches, current_branch):
        """
        Callback for background Git checks. Populates Git panel if repository is found.
        """
        if hasattr(self, 'git_panel'):
            if is_repo:
                self.git_panel.stack.setCurrentWidget(self.git_panel.repo_widget)
                self.git_panel.refresh(status, branches, current_branch)
                self.status_git_label.setText(current_branch or "")
            else:
                self.git_panel.stack.setCurrentWidget(self.git_panel.no_repo_widget)
                self.status_git_label.setText("")

    def create_activity_bar(self):
        """
        Constructs the vertical activity bar for primary section toggling (Explorer, Search, etc).
        """
        activity_bar = QToolBar("Activity Bar")
        activity_bar.setMovable(False)
        activity_bar.setFloatable(False)
        activity_bar.setOrientation(Qt.Orientation.Vertical)
        activity_bar.setIconSize(QSize(28, 28))
        activity_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, activity_bar)
        
        # Explorer Toggle
        self.explorer_action = QAction(load_icon("folder.svg"), "Explorer", self)
        self.explorer_action.setCheckable(True)
        self.explorer_action.setChecked(True)
        self.explorer_action.triggered.connect(lambda: self.toggle_view("explorer"))
        activity_bar.addAction(self.explorer_action)
        
        # Search Toggle
        self.search_action = QAction(load_icon("search.svg"), "Search", self)
        self.search_action.setCheckable(True)
        self.search_action.triggered.connect(lambda: self.toggle_view("search"))
        activity_bar.addAction(self.search_action)
        
        # Git Toggle
        self.git_action = QAction(load_icon("git.svg"), "Source Control", self)
        self.git_action.setCheckable(True)
        self.git_action.triggered.connect(lambda: self.toggle_view("git"))
        activity_bar.addAction(self.git_action)

        # Extensions Toggle
        self.extensions_action = QAction(load_icon("extensions.svg"), "Extensions", self)
        self.extensions_action.setCheckable(True)
        self.extensions_action.triggered.connect(lambda: self.toggle_view("extensions"))
        activity_bar.addAction(self.extensions_action)
        
        # Debugger Toggle
        self.debug_action = QAction(load_icon("debug.svg"), "Run and Debug", self)
        self.debug_action.setCheckable(True)
        self.debug_action.triggered.connect(lambda: self.toggle_view("debug"))
        activity_bar.addAction(self.debug_action)
        
        # Logs Toggle
        self.logs_action = QAction(load_icon("output.svg"), "App Logs", self)
        self.logs_action.setCheckable(True)
        self.logs_action.triggered.connect(lambda: self.toggle_view("logs"))
        activity_bar.addAction(self.logs_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        activity_bar.addWidget(spacer)

        # Bottom Settings Action
        settings_action = QAction(load_icon("settings.svg"), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        activity_bar.addAction(settings_action)

    def open_settings(self):
        """
        Opens the global settings dialog.
        """
        from core.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self, api_handler=self.ai_widget.api_model_handler)
        dialog.exec()

    def toggle_view(self, view_name):
        """
        Manages sidebar visibility and stack switching based on activity bar interaction.
        """
        sidebar_config = {
            "explorer": {"action": self.explorer_action, "index": 0, "title": "EXPLORER"},
            "git": {"action": self.git_action, "index": 1, "title": "SOURCE CONTROL"},
            "logs": {"action": self.logs_action, "index": 2, "title": "APP LOGS"},
            "extensions": {"action": self.extensions_action, "index": 3, "title": "EXTENSIONS"},
            "search": {"action": self.search_action, "index": 4, "title": "SEARCH"},
            "debug": {"action": self.debug_action, "index": 5, "title": "DEBUG"},
        }
        
        if view_name not in sidebar_config: return
        
        target = sidebar_config[view_name]
        action = target["action"]
        
        if action.isChecked():
            # If sidebar is already visible and showing this view, toggle it off
            if self.sidebar_dock.isVisible() and self.sidebar_stack.currentIndex() == target["index"]:
                self.sidebar_dock.setVisible(False)
                action.setChecked(False)
            else:
                # Uncheck others
                for name, cfg in sidebar_config.items():
                    if name != view_name: cfg["action"].setChecked(False)
                
                # Show sidebar and switch to targeted view
                self.sidebar_dock.setVisible(True)
                self.sidebar_stack.setCurrentIndex(target["index"])
                self.sidebar_dock.setWindowTitle(target["title"])
                
                # Trigger lazy refreshes
                if view_name == "git": self.git_panel.refresh()
                if view_name == "search" and self.project_path: self.search_panel.set_project_path(self.project_path)
        else:
            self.sidebar_dock.setVisible(False)

    def create_status_bar(self):
        """
        Initializes the application status bar with project and cursor information.
        """
        status_bar = QStatusBar()
        status_bar.setFixedHeight(22)
        self.setStatusBar(status_bar)
        
        self.status_git_label = QLabel("")
        self.status_git_label.setObjectName("StatusFirst")
        status_bar.addWidget(self.status_git_label)
        
        self.status_file_label = QLabel("No file open")
        status_bar.addWidget(self.status_file_label)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        status_bar.addWidget(spacer, 1)
        
        # Python Environment Selector
        self.status_env_button = QPushButton("Python")
        self.status_env_button.setObjectName("StatusRight")
        self.status_env_button.setFlat(True)
        self.status_env_button.clicked.connect(self.open_env_selection)
        status_bar.addWidget(self.status_env_button)

        self.status_cursor_label = QLabel("Ln 1, Col 1")
        self.status_cursor_label.setObjectName("StatusRight")
        status_bar.addWidget(self.status_cursor_label)
        
        self.status_encoding_label = QLabel("UTF-8")
        self.status_encoding_label.setObjectName("StatusRight")
        status_bar.addWidget(self.status_encoding_label)
        
        self.status_language_label = QLabel("Plain Text")
        self.status_language_label.setObjectName("StatusRight")
        status_bar.addWidget(self.status_language_label)

    def create_menu_bar(self):
        """
        Delegates menu bar construction to the MenuManager.
        """
        self.menu_manager = MenuManager(self)
        self.menu_manager.setup_menu_bar()

    def update_status_bar(self):
        """
        Updates file path and language metadata in the status bar based on the active editor.
        """
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'file_path'):
            filename = os.path.basename(editor.file_path)
            self.status_file_label.setText(filename)
            
            ext = os.path.splitext(filename)[1].lower()
            lang_map = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.html': 'HTML', '.css': 'CSS', '.json': 'JSON', '.md': 'Markdown'}
            self.status_language_label.setText(lang_map.get(ext, 'Plain Text'))
            
            line, col = editor.getCursorPosition()
            self.update_cursor_position(line, col)
        else:
            self.status_file_label.setText("No file open")
            self.status_language_label.setText("—")
            self.status_cursor_label.setText("Ln 1, Col 1")

    def update_cursor_position(self, line, col):
        """
        Updates line and column coordinates in the status bar.
        """
        self.status_cursor_label.setText(f"Ln {line + 1}, Col {col + 1}")

    def open_file_dialog(self):
        """
        Prompts user to select a file from the system to open in the IDE.
        """
        start_dir = self.project_path or os.getcwd()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", start_dir)
        if file_path:
            self.open_file_in_tab(file_path)
            self._update_last_open_folder(os.path.dirname(file_path))

    def open_folder_dialog(self):
        """
        Prompts user to select a project root directory.
        """
        folder = QFileDialog.getExistingDirectory(self, "Open Folder", self.project_path)
        if not folder: return

        self.editor_manager.close_all_tabs()
        self.project_path = folder
        self._update_last_open_folder(folder)

        # Update dependent managers
        self.env_manager.set_project_path(folder)
        self.dep_manager.project_path = folder
        self.update_env_status()

        if hasattr(self.sidebar, "set_root_path"): self.sidebar.set_root_path(folder)
        if hasattr(self, 'git_panel'): self.git_panel.set_repository(folder)
        
        # Update AI Context Manager and trigger re-index
        if hasattr(self, 'ai_widget'):
            self.ai_widget.context_manager.set_project_path(folder)
            # Indexing will happen on demand or via Background thread
            # For now, let's trigger a one-time index if RAG is on
            if self.ai_widget.context_manager.rag_enabled:
                self.ai_widget.context_manager.rag_manager.index_project()

    def open_file_in_tab(self, file_path: str, line_number: int = None):
        """
        Logic for opening a file and optionally jumping to a specific line.
        """
        self.editor_manager.open_file(file_path)
        if line_number is not None:
             editor = self.get_current_editor()
             if editor:
                 editor.setCursorPosition(line_number - 1, 0)
                 editor.ensureLineVisible(line_number - 1)
                 editor.setFocus()

    def get_current_editor(self):
        """
        Retrieves the CodeEditor widget from the currently selected tab.
        """
        return self.editor_manager.get_current_editor()

    def execute_current_file(self):
        """
        Saves and executes buffered code in the project environment's shell.
        """
        editor = self.get_current_editor()
        if not editor: return

        file_path = getattr(editor, "file_path", None)
        if not file_path:
            import tempfile
            fd, file_path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, "w") as f: f.write(editor.text())
        else:
            with open(file_path, "w", encoding="utf-8") as f: f.write(editor.text())

        terminal = self.terminal_tabs.currentWidget()
        if terminal and hasattr(terminal, "execute_command"):
            python_exec = self.env_manager.get_active_env()
            terminal.execute_command(f"\"{python_exec}\" \"{file_path}\"")

    def add_terminal_tab(self, name="Terminal"):
        """
        Appends a new shell terminal tab.
        """
        term = Terminal(project_path=self.project_path)
        self.terminal_tabs.addTab(term, name)

    def _load_settings(self):
        """
        Reads application settings from disk.
        """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception: pass
        return {}

    def _save_settings(self):
        """
        Persists application settings to disk.
        """
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except Exception: pass

    def _update_last_open_folder(self, folder):
        """
        Tracks the most recently opened folder for session persistence.
        """
        if folder:
            self.project_path = folder
            self._settings["last_open_folder"] = folder
            self._save_settings()

    def setup_keybindings(self):
        """
        Registers all global system shortcuts.
        """
        self.keybindings.register("file.open", self.open_file_dialog, self)
        self.keybindings.register("file.open_folder", self.open_folder_dialog, self)
        self.keybindings.register("file.save", lambda: self.editor_manager.save_current_file(), self)
        self.keybindings.register("app.quick_open", self.show_quick_open, self)
        self.keybindings.register("app.command_palette", self.show_command_palette, self)

    def show_quick_open(self):
        """
        Displays the fuzzy file search palette.
        """
        from core.ui.command_palette import CommandPalette
        palette = CommandPalette(self, mode="files", project_path=self.project_path)
        palette.exec()

    def show_command_palette(self):
        """
        Displays the global action selection palette.
        """
        from core.ui.command_palette import CommandPalette
        commands = [
            ("Open File", self.open_file_dialog),
            ("Open Folder", self.open_folder_dialog),
            ("Run File", self.execute_current_file),
            ("Settings", self.open_settings),
        ]
        palette = CommandPalette(self, mode="commands", actions=commands)
        palette.exec()

    def update_env_status(self):
        """
        Refreshes the environment selector display name.
        """
        active_env = self.env_manager.get_active_env()
        self.status_env_button.setText(os.path.basename(os.path.dirname(active_env)) or "Default Python")

    def open_env_selection(self):
        """
        Opens a dialog to switch Python interpreters.
        """
        dialog = EnvironmentSelectionDialog(self, self.env_manager, self.env_manager.get_active_env())
        dialog.env_selected.connect(self.on_env_selected)
        dialog.exec()

    def on_env_selected(self, name, path):
        """
        Sets the active Python environment for execution and linting.
        """
        self.env_manager.set_active_env(path)
        self.update_env_status()

    def exit_application(self):
        """
        Closes the main application window.
        """
        self.close()

    def show_about(self):
        """
        Displays the About dialog for the application.
        """
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About PyCursor", 
                         "PyCursor IDE\n\nA modern Python IDE built with PyQt6.\n\nVersion 1.0.0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
