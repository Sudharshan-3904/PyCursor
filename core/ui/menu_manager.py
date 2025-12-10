"""
Menu Manager Module

This module handles the construction and management of the main application menu bar.
It encapulates the logic for creating menus (File, Edit, View, etc.) and connecting
actions to their respective handlers in the main application.
"""
from PyQt6.QtWidgets import QMenu, QApplication, QWidget, QHBoxLayout, QPushButton
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from core.utilities.utils import load_icon
from core.ui.theme import COLORS
from core.ui.keybindings_dialog import KeybindingsDialog

class MenuManager:
    """
    Manages the application's menu bar and corner widgets.
    
    This class constructs the standard menu hierarchy and a custom corner widget
    for quick view toggling. It interacts with the main window to connect actions
    and retrieve keybindings.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def setup_menu_bar(self):
        menu_bar = self.main_window.menuBar()
        menu_bar.clear() # Clear existing if any
        
        # --- File Menu ---
        file_menu = menu_bar.addMenu("&File")

        new_file_action = QAction("New Text File", self.main_window)
        new_file_action.setShortcut("Ctrl+N")
        new_file_action.triggered.connect(lambda: self.main_window.editor_manager.open_file(None)) 
        file_menu.addAction(new_file_action)

        open_action = QAction("&Open File...", self.main_window)
        # Using getattr to avoid crashes if keybindings aren't set, though they should be
        kb = self.main_window.keybindings
        open_action.setShortcut(kb.get("file.open"))
        open_action.triggered.connect(self.main_window.open_file_dialog)
        file_menu.addAction(open_action)

        open_folder_action = QAction("Open &Folder...", self.main_window)
        open_folder_action.setShortcut(kb.get("file.open_folder"))
        open_folder_action.triggered.connect(self.main_window.open_folder_dialog)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()

        save_action = QAction("&Save", self.main_window)
        save_action.setShortcut(kb.get("file.save"))
        save_action.triggered.connect(self.main_window.editor_manager.save_current_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self.main_window)
        save_as_action.setShortcut(kb.get("file.save_as"))
        save_as_action.triggered.connect(lambda: self.main_window.editor_manager.save_current_file(save_as=True))
        file_menu.addAction(save_as_action)
        
        save_all_action = QAction("Save A&ll", self.main_window)
        save_all_action.triggered.connect(self.main_window.editor_manager.save_all_files)
        file_menu.addAction(save_all_action)
        
        file_menu.addSeparator()
        
        # Preferences Submenu
        pref_menu = file_menu.addMenu("Preferences")
        settings_action = QAction("Settings", self.main_window)
        settings_action.setShortcut(kb.get("app.settings"))
        settings_action.triggered.connect(self.main_window.open_settings)
        pref_menu.addAction(settings_action)
        
        keybindings_action = QAction("Keyboard Shortcuts", self.main_window)
        keybindings_action.triggered.connect(lambda: KeybindingsDialog(self.main_window, self.main_window.keybindings).exec())
        pref_menu.addAction(keybindings_action)

        file_menu.addSeparator()
        
        close_tab_action = QAction("&Close Tab", self.main_window)
        close_tab_action.setShortcut(kb.get("file.close_tab"))
        close_tab_action.triggered.connect(lambda: self.main_window.editor_manager.close_tab(self.main_window.editor_tabs.currentIndex()))
        file_menu.addAction(close_tab_action)
        
        exit_action = QAction("E&xit", self.main_window)
        exit_action.triggered.connect(self.main_window.exit_application)
        file_menu.addAction(exit_action)

        # --- Edit Menu ---
        edit_menu = menu_bar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self.main_window)
        undo_action.setShortcut(kb.get_sequence("edit.undo"))
        # Undo/Redo often depend on focus, so QApplication.focusWidget() is correct or current editor
        undo_action.triggered.connect(lambda: QApplication.focusWidget().undo() if hasattr(QApplication.focusWidget(), "undo") else None)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self.main_window)
        redo_action.setShortcut(kb.get_sequence("edit.redo"))
        redo_action.triggered.connect(lambda: QApplication.focusWidget().redo() if hasattr(QApplication.focusWidget(), "redo") else None)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self.main_window)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda: QApplication.focusWidget().cut() if hasattr(QApplication.focusWidget(), "cut") else None)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self.main_window)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: QApplication.focusWidget().copy() if hasattr(QApplication.focusWidget(), "copy") else None)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self.main_window)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: QApplication.focusWidget().paste() if hasattr(QApplication.focusWidget(), "paste") else None)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find", self.main_window)
        find_action.setShortcut(kb.get_sequence("edit.find"))
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace", self.main_window)
        replace_action.setShortcut(kb.get_sequence("edit.replace"))
        edit_menu.addAction(replace_action)

        # --- Selection Menu ---
        selection_menu = menu_bar.addMenu("&Selection")
        select_all_action = QAction("Select All", self.main_window)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(lambda: QApplication.focusWidget().selectAll() if hasattr(QApplication.focusWidget(), "selectAll") else None)
        selection_menu.addAction(select_all_action)

        # --- View Menu ---
        view_menu = menu_bar.addMenu("&View")
        
        command_palette_action = QAction("Command &Palette", self.main_window)
        command_palette_action.setShortcut(kb.get_sequence("app.command_palette"))
        command_palette_action.triggered.connect(self.main_window.show_command_palette)
        view_menu.addAction(command_palette_action)
        
        view_menu.addSeparator()
        
        appearance_menu = view_menu.addMenu("Appearance")
        toggle_sidebar = QAction("Show Sidebar", self.main_window, checkable=True)
        toggle_sidebar.setChecked(self.main_window.sidebar_dock.isVisible())
        toggle_sidebar.triggered.connect(lambda c: self.main_window.sidebar_dock.setVisible(c))
        self.main_window.sidebar_dock.visibilityChanged.connect(toggle_sidebar.setChecked)
        appearance_menu.addAction(toggle_sidebar)
        
        toggle_terminal = QAction("Show Panel", self.main_window, checkable=True)
        toggle_terminal.setChecked(self.main_window.terminal_dock.isVisible())
        toggle_terminal.triggered.connect(lambda c: self.main_window.terminal_dock.setVisible(c))
        self.main_window.terminal_dock.visibilityChanged.connect(toggle_terminal.setChecked)
        appearance_menu.addAction(toggle_terminal)
        
        toggle_ai = QAction("Show AI Assistant", self.main_window, checkable=True)
        toggle_ai.setChecked(self.main_window.ai_dock.isVisible())
        toggle_ai.triggered.connect(lambda c: self.main_window.ai_dock.setVisible(c))
        self.main_window.ai_dock.visibilityChanged.connect(toggle_ai.setChecked)
        appearance_menu.addAction(toggle_ai)
        
        view_menu.addSeparator()
        
        explore_view = QAction("Explorer", self.main_window)
        explore_view.setShortcut(kb.get_sequence("view.toggle_explorer"))
        explore_view.triggered.connect(lambda: self.main_window.toggle_view("explorer"))
        view_menu.addAction(explore_view)
        
        search_view = QAction("Search", self.main_window)
        search_view.triggered.connect(lambda: self.main_window.toggle_view("search"))
        view_menu.addAction(search_view)
        
        scm_view = QAction("Source Control", self.main_window)
        scm_view.triggered.connect(lambda: self.main_window.toggle_view("git"))
        view_menu.addAction(scm_view)
        
        # --- Go Menu ---
        go_menu = menu_bar.addMenu("&Go")
        go_file_action = QAction("Go to &File...", self.main_window)
        go_file_action.setShortcut(kb.get("app.quick_open"))
        go_file_action.triggered.connect(self.main_window.show_quick_open)
        go_menu.addAction(go_file_action)

        # --- Run Menu ---
        run_menu = menu_bar.addMenu("&Run")
        run_action = QAction("Run &Without Debugging", self.main_window)
        run_action.setShortcut(kb.get_sequence("run.run_code"))
        run_action.triggered.connect(self.main_window.execute_current_file)
        run_menu.addAction(run_action)
        
        # --- Terminal Menu ---
        term_menu = menu_bar.addMenu("&Terminal")
        new_term_action = QAction("New Terminal", self.main_window)
        new_term_action.triggered.connect(lambda: self.main_window.add_terminal_tab(f"Terminal {self.main_window.terminal_tabs.count() + 1}"))
        term_menu.addAction(new_term_action)
        
        # --- Help Menu ---
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("About", self.main_window)
        about_action.triggered.connect(self.main_window.show_about)
        help_menu.addAction(about_action)

        # --- Corner Widget for Menu Bar (View Toggles) ---
        self.setup_corner_widget(menu_bar)

    def setup_corner_widget(self, menu_bar):
        corner_widget = QWidget()
        corner_layout = QHBoxLayout()
        corner_layout.setContentsMargins(0, 0, 5, 0)
        corner_layout.setSpacing(5)
        corner_widget.setLayout(corner_layout)

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
        self.sidebar_toggle_btn.setChecked(self.main_window.sidebar_dock.isVisible())
        self.sidebar_toggle_btn.clicked.connect(lambda checked: self.main_window.sidebar_dock.setVisible(checked))
        self.main_window.sidebar_dock.visibilityChanged.connect(self.sidebar_toggle_btn.setChecked)
        self.sidebar_toggle_btn.setStyleSheet(btn_style)
        corner_layout.addWidget(self.sidebar_toggle_btn)

        self.terminal_toggle_btn = QPushButton("⌨")
        self.terminal_toggle_btn.setCheckable(True)
        self.terminal_toggle_btn.setChecked(self.main_window.terminal_dock.isVisible())
        self.terminal_toggle_btn.clicked.connect(lambda checked: self.main_window.terminal_dock.setVisible(checked))
        self.main_window.terminal_dock.visibilityChanged.connect(self.terminal_toggle_btn.setChecked)
        self.terminal_toggle_btn.setStyleSheet(btn_style)
        corner_layout.addWidget(self.terminal_toggle_btn)

        self.ai_toggle_btn = QPushButton("✨")
        self.ai_toggle_btn.setCheckable(True)
        self.ai_toggle_btn.setChecked(self.main_window.ai_dock.isVisible())
        self.ai_toggle_btn.clicked.connect(lambda checked: self.main_window.ai_dock.setVisible(checked))
        self.main_window.ai_dock.visibilityChanged.connect(self.ai_toggle_btn.setChecked)
        self.ai_toggle_btn.setStyleSheet(btn_style)
        corner_layout.addWidget(self.ai_toggle_btn)
        
        menu_bar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)
