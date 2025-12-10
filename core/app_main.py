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


class StartupThread(QThread):
    models_ready = pyqtSignal(dict)
    git_ready = pyqtSignal(bool, object, object, object) # is_repo, status, branches, current_branch

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

    def run(self):
        # 1. Detect AI Models
        try:
            handler = LocalModelHandler()
            models = handler.detect_models()
            self.models_ready.emit(models)
        except Exception as e:
            print(f"Model detection failed: {e}")
            self.models_ready.emit({})

        # 2. Check Git Status
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
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.setDocumentMode(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.setCentralWidget(self.editor_tabs)

        # Create Stacked Widget for Sidebar (Explorer, Git, etc.)
        self.sidebar_stack = QStackedWidget()

        # 1. File Explorer
        self.sidebar = SideBar(root_path=self.project_path)
        self.sidebar.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.sidebar)

        # 2. Git Panel
        self.git_panel = GitPanel(repo_path=self.project_path)
        self.git_panel.file_selected.connect(self.open_file_in_tab)
        self.sidebar_stack.addWidget(self.git_panel)

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

    def on_git_ready(self, is_repo, status, branches, current_branch):
        if hasattr(self, 'git_panel'):
            if is_repo:
                self.git_panel.stack.setCurrentWidget(self.git_panel.repo_widget)
                self.git_panel.refresh(status, branches, current_branch)
                if current_branch:
                    self.status_git_label.setText(current_branch)
            else:
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
                    elif view_name == "search":
                        # self.sidebar_stack.setCurrentIndex(2)
                        self.sidebar_dock.setWindowTitle("SEARCH")
                        pass
            else:
                self.sidebar_dock.setVisible(False)
                current_action.setProperty("was_active", False)
    
    
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
        open_action.setShortcut(self.keybindings.get("file.open"))
        open_action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        open_action.triggered.connect(self.open_file_dialog)

        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut(self.keybindings.get("file.open_folder"))
        open_folder_action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        open_folder_action.triggered.connect(self.open_folder_dialog)

        save_action = QAction("&Save", self)
        save_action.setShortcut(self.keybindings.get("file.save"))
        save_action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        save_action.triggered.connect(self.save_file)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(self.keybindings.get("file.save_as"))
        save_as_action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        save_as_action.triggered.connect(lambda: self.save_file(save_as=True))

        file_menu.addAction(open_action)
        file_menu.addAction(open_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        
        close_tab_action = QAction("&Close Tab", self)
        close_tab_action.setShortcut(self.keybindings.get("file.close_tab"))
        close_tab_action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        close_tab_action.triggered.connect(lambda: self.close_editor_tab(self.editor_tabs.currentIndex()))
        file_menu.addAction(close_tab_action)

        edit_menu = menu_bar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(self.keybindings.get_sequence("edit.undo"))
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(self.keybindings.get_sequence("edit.redo"))
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find", self)
        find_action.setShortcut(self.keybindings.get_sequence("edit.find"))
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace", self)
        replace_action.setShortcut(self.keybindings.get_sequence("edit.replace"))
        edit_menu.addAction(replace_action)

        view_menu = menu_bar.addMenu("&View")
        
        toggle_sidebar_action = QAction("Toggle &Explorer", self)
        toggle_sidebar_action.setShortcut(self.keybindings.get_sequence("view.toggle_explorer"))
        toggle_sidebar_action.triggered.connect(lambda: self.sidebar_dock.setVisible(not self.sidebar_dock.isVisible()))
        view_menu.addAction(toggle_sidebar_action)
        
        toggle_terminal_action = QAction("Toggle &Terminal", self)
        toggle_terminal_action.setShortcut(self.keybindings.get_sequence("view.toggle_terminal"))
        toggle_terminal_action.triggered.connect(lambda: self.terminal_dock.setVisible(not self.terminal_dock.isVisible()))
        view_menu.addAction(toggle_terminal_action)
        
        toggle_ai_action = QAction("Toggle &AI Assistant", self)
        toggle_ai_action.setShortcut(self.keybindings.get_sequence("view.toggle_ai"))
        toggle_ai_action.triggered.connect(lambda: self.ai_dock.setVisible(not self.ai_dock.isVisible()))
        view_menu.addAction(toggle_ai_action)
        
        view_menu.addSeparator()
        
        command_palette_action = QAction("Command &Palette", self)
        command_palette_action.setShortcut(self.keybindings.get_sequence("app.command_palette"))
        command_palette_action.triggered.connect(self.show_command_palette)
        view_menu.addAction(command_palette_action)

        run_menu = menu_bar.addMenu("&Run")
        run_action = QAction("&Run Code", self)
        run_action.setShortcut(self.keybindings.get_sequence("run.run_code"))
        run_action.triggered.connect(self.execute_current_file)
        run_menu.addAction(run_action)

        # --- Corner Widget for Menu Bar (View Toggles) ---
        corner_widget = QWidget()
        corner_layout = QHBoxLayout()
        corner_layout.setContentsMargins(0, 0, 5, 0)
        corner_layout.setSpacing(5)
        corner_widget.setLayout(corner_layout)

        # Re-using the styles from the old toolbar for consistency
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 3px 8px;
                color: {COLORS['text_primary']};
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border_light']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['accent_blue']};
            }}
        """

        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setCheckable(True)
        self.sidebar_toggle_btn.setChecked(self.sidebar_dock.isVisible())
        self.sidebar_toggle_btn.clicked.connect(lambda checked: self.sidebar_dock.setVisible(checked))
        self.sidebar_dock.visibilityChanged.connect(self.sidebar_toggle_btn.setChecked)
        self.sidebar_toggle_btn.setStyleSheet(btn_style)
        corner_layout.addWidget(self.sidebar_toggle_btn)

        self.terminal_toggle_btn = QPushButton("⌨")
        self.terminal_toggle_btn.setCheckable(True)
        self.terminal_toggle_btn.setChecked(self.terminal_dock.isVisible())
        self.terminal_toggle_btn.clicked.connect(lambda checked: self.terminal_dock.setVisible(checked))
        self.terminal_dock.visibilityChanged.connect(self.terminal_toggle_btn.setChecked)
        self.terminal_toggle_btn.setStyleSheet(btn_style)
        corner_layout.addWidget(self.terminal_toggle_btn)

        self.ai_toggle_btn = QPushButton("✨")
        self.ai_toggle_btn.setCheckable(True)
        self.ai_toggle_btn.setChecked(self.ai_dock.isVisible())
        self.ai_toggle_btn.clicked.connect(lambda checked: self.ai_dock.setVisible(checked))
        self.ai_dock.visibilityChanged.connect(self.ai_toggle_btn.setChecked)
        self.ai_toggle_btn.setStyleSheet(btn_style)
        corner_layout.addWidget(self.ai_toggle_btn)
        
        menu_bar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)
    
    
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
            
        # Update Git Panel
        if hasattr(self, 'git_panel'):
            self.git_panel.set_repository(folder)

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
        
        # Connect Git signals
        editor.git_blame_requested.connect(self.show_git_blame)
        editor.git_history_requested.connect(self.show_git_history)

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

    def show_git_blame(self, file_path: str):
        """Show Git blame for the file"""
        if not hasattr(self, 'git_panel') or not self.git_panel.git_handler.repo:
            QMessageBox.information(self, "Git Info", "Not a git repository.")
            return
        
        blame_data = self.git_panel.git_handler.get_file_blame(file_path)
        if blame_data:
            from core.ui.git_dialogs import GitBlameDialog
            dialog = GitBlameDialog(os.path.basename(file_path), blame_data, self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Git Info", "No blame information available.")

    def show_git_history(self, file_path: str):
        """Show Git history for the file"""
        if not hasattr(self, 'git_panel') or not self.git_panel.git_handler.repo:
            QMessageBox.information(self, "Git Info", "Not a git repository.")
            return
            
        history_data = self.git_panel.git_handler.get_file_history(file_path)
        if history_data:
            from core.ui.git_dialogs import GitHistoryDialog
            dialog = GitHistoryDialog(os.path.basename(file_path), history_data, self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Git Info", "No history available.")

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
