from PyQt6.QtWidgets import QMenu, QApplication, QWidget, QHBoxLayout, QPushButton
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from core.utilities.utils import load_icon
from core.ui.theme import THEMES
from core.ui.keybindings_dialog import KeybindingsDialog

class MenuManager:
    """
    Orchestrates the construction and event-binding of the application's top-level menu system.
    Standardizes menu categories and integrates keyboard shortcuts with system actions.
    """
    def __init__(self, main_window):
        """
        Initializes the manager with a target main window for signal connection.
        """
        self.main_window = main_window

    def setup_menu_bar(self):
        """
        Populates the application menu bar with categories: File, Edit, Selection, View, Go, Run, Terminal, Help.
        """
        menu_bar = self.main_window.menuBar()
        menu_bar.clear()
        kb = self.main_window.keybindings
        
        # --- File Section ---
        file_menu = menu_bar.addMenu("&File")

        new_file = QAction("New Text File", self.main_window)
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(lambda: self.main_window.editor_manager.open_file(None)) 
        file_menu.addAction(new_file)

        open_file = QAction("&Open File...", self.main_window)
        open_file.setShortcut(kb.get("file.open"))
        open_file.triggered.connect(self.main_window.open_file_dialog)
        file_menu.addAction(open_file)

        open_folder = QAction("Open &Folder...", self.main_window)
        open_folder.setShortcut(kb.get("file.open_folder"))
        open_folder.triggered.connect(self.main_window.open_folder_dialog)
        file_menu.addAction(open_folder)
        
        file_menu.addSeparator()

        save = QAction("&Save", self.main_window)
        save.setShortcut(kb.get("file.save"))
        save.triggered.connect(self.main_window.editor_manager.save_current_file)
        file_menu.addAction(save)
        
        save_all = QAction("Save A&ll", self.main_window)
        save_all.triggered.connect(self.main_window.editor_manager.save_all_files)
        file_menu.addAction(save_all)
        
        file_menu.addSeparator()
        
        # Application Preferences Submenu
        pref_menu = file_menu.addMenu("Preferences")
        settings = QAction("Settings", self.main_window)
        settings.setShortcut(kb.get("app.settings"))
        settings.triggered.connect(self.main_window.open_settings)
        pref_menu.addAction(settings)
        
        kb_shortcut = QAction("Keyboard Shortcuts", self.main_window)
        kb_shortcut.triggered.connect(lambda: KeybindingsDialog(self.main_window, self.main_window.keybindings).exec())
        pref_menu.addAction(kb_shortcut)

        file_menu.addSeparator()
        
        close_tab = QAction("&Close Tab", self.main_window)
        close_tab.setShortcut(kb.get("file.close_tab"))
        close_tab.triggered.connect(lambda: self.main_window.editor_manager.close_tab(self.main_window.editor_tabs.currentIndex()))
        file_menu.addAction(close_tab)
        
        exit_app = QAction("E&xit", self.main_window)
        exit_app.triggered.connect(self.main_window.exit_application)
        file_menu.addAction(exit_app)

        # --- Edit Section ---
        edit_menu = menu_bar.addMenu("&Edit")
        
        undo = QAction("&Undo", self.main_window)
        undo.setShortcut(kb.get_sequence("edit.undo"))
        undo.triggered.connect(lambda: QApplication.focusWidget().undo() if hasattr(QApplication.focusWidget(), "undo") else None)
        edit_menu.addAction(undo)
        
        redo = QAction("&Redo", self.main_window)
        redo.setShortcut(kb.get_sequence("edit.redo"))
        redo.triggered.connect(lambda: QApplication.focusWidget().redo() if hasattr(QApplication.focusWidget(), "redo") else None)
        edit_menu.addAction(redo)
        
        edit_menu.addSeparator()
        
        cut = QAction("Cut", self.main_window)
        cut.setShortcut("Ctrl+X")
        cut.triggered.connect(lambda: QApplication.focusWidget().cut() if hasattr(QApplication.focusWidget(), "cut") else None)
        edit_menu.addAction(cut)
        
        copy = QAction("Copy", self.main_window)
        copy.setShortcut("Ctrl+C")
        copy.triggered.connect(lambda: QApplication.focusWidget().copy() if hasattr(QApplication.focusWidget(), "copy") else None)
        edit_menu.addAction(copy)
        
        paste = QAction("Paste", self.main_window)
        paste.setShortcut("Ctrl+V")
        paste.triggered.connect(lambda: QApplication.focusWidget().paste() if hasattr(QApplication.focusWidget(), "paste") else None)
        edit_menu.addAction(paste)

        # --- View Section ---
        view_menu = menu_bar.addMenu("&View")
        
        palette = QAction("Command &Palette", self.main_window)
        palette.setShortcut(kb.get_sequence("app.command_palette"))
        palette.triggered.connect(self.main_window.show_command_palette)
        view_menu.addAction(palette)
        
        view_menu.addSeparator()
        
        # View Visibility Submenu
        open_view = view_menu.addMenu("Open View")
        views = [("Explorer", "explorer"), ("Search", "search"), ("Source Control", "git"), ("Extensions", "extensions"), ("Output", "logs")]
        for label, vid in views:
            act = QAction(label, self.main_window)
            act.triggered.connect(lambda checked, v=vid: self.main_window.toggle_view(v))
            open_view.addAction(act)

        # Appearance Submenu
        appearance = view_menu.addMenu("Appearance")
        theme_menu = appearance.addMenu("Color Theme")
        
        # Dynamically populate theme menu from the design system's registry
        for tid, tinfo in THEMES.items():
            theme_menu.addAction(tinfo['name'], lambda checked, t=tid: self.main_window.apply_theme(t))

        view_menu.addSeparator()
        
        zoom_in = QAction("Zoom In", self.main_window)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.triggered.connect(lambda: self.main_window.get_current_editor().zoomIn() if self.main_window.get_current_editor() else None)
        view_menu.addAction(zoom_in)
        
        zoom_out = QAction("Zoom Out", self.main_window)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(lambda: self.main_window.get_current_editor().zoomOut() if self.main_window.get_current_editor() else None)
        view_menu.addAction(zoom_out)

        # --- Go Section ---
        go_menu = menu_bar.addMenu("&Go")
        go_file = QAction("Go to &File...", self.main_window)
        go_file.setShortcut(kb.get("app.quick_open"))
        go_file.triggered.connect(self.main_window.show_quick_open)
        go_menu.addAction(go_file)
        
        go_line = QAction("Go to Line/Column...", self.main_window)
        go_line.setShortcut("Ctrl+G")
        go_line.triggered.connect(self.main_window.show_go_to_line)
        go_menu.addAction(go_line)

        # --- Terminal Section ---
        term_menu = menu_bar.addMenu("&Terminal")
        new_term = QAction("New Terminal", self.main_window)
        new_term.triggered.connect(lambda: self.main_window.add_terminal_tab(f"Terminal {self.main_window.terminal_tabs.count() + 1}"))
        term_menu.addAction(new_term)
        
        term_menu.addSeparator()
        
        clear_term = QAction("Clear Terminal", self.main_window)
        clear_term.triggered.connect(lambda: self.main_window.terminal_tabs.currentWidget().execute_command("clear") if self.main_window.terminal_tabs.currentWidget() else None)
        term_menu.addAction(clear_term)

        # --- Help Section ---
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("Welcome", lambda: self.main_window.show_welcome_screen(force=True))
        help_menu.addAction("About", self.main_window.show_about)

        self.setup_corner_widget(menu_bar)

    def setup_corner_widget(self, menu_bar):
        """
        Integrates quick-toggle buttons into the right-hand side of the menu bar.
        """
        corner_widget = QWidget()
        layout = QHBoxLayout(corner_widget)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(5)

        # Helper to bind dock visibility to a button
        def bind_toggle(btn, dock):
            btn.setCheckable(True)
            btn.setChecked(dock.isVisible())
            btn.clicked.connect(dock.setVisible)
            dock.visibilityChanged.connect(btn.setChecked)

        self.sidebar_toggle = QPushButton("☰")
        bind_toggle(self.sidebar_toggle, self.main_window.sidebar_dock)
        layout.addWidget(self.sidebar_toggle)

        self.terminal_toggle = QPushButton("⌨")
        bind_toggle(self.terminal_toggle, self.main_window.terminal_dock)
        layout.addWidget(self.terminal_toggle)

        self.ai_toggle = QPushButton("✨")
        bind_toggle(self.ai_toggle, self.main_window.ai_dock)
        layout.addWidget(self.ai_toggle)
        
        menu_bar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)
