"""
Editor Manager Module

This module is responsible for managing the text editor tabs within the PyCursor IDE.
It handles opening files, saving files, closing tabs, and managing the state of the
QTabWidget that holds the editors.
"""
import os
from PyQt6.QtWidgets import QTabWidget, QMessageBox, QFileDialog, QPushButton, QTabBar, QApplication
from core.ui.editor import CodeEditor
from core.utilities.utils import load_icon

class EditorManager:
    """
    Manages the lifecycle of code editor tabs.
    
    This class serves as a controller for the main editor area. It abstracts away
    the details of QTabWidget manipulation and file I/O from the main window.
    It also connects editor-specific signals (like cursor changes or Git requests)
    to the appropriate handlers in the main application.
    """
    def __init__(self, main_window, tab_widget: QTabWidget):
        self.main_window = main_window
        self.tabs = tab_widget
        self.setup_tabs()

    def setup_tabs(self):
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        # We need to connect the signal in main_window or here. 
        # Better here if we want to encapsulate fully, but main_window currently connects it.
        # Let's keep the signal connection control in main_window or expose a method.
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if hasattr(self.main_window, 'update_status_bar'):
            self.main_window.update_status_bar()

    def get_current_editor(self) -> CodeEditor:
        editor = self.tabs.currentWidget()
        if isinstance(editor, CodeEditor):
            return editor
        return None

    def open_file(self, file_path: str):
        # check if already open
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if getattr(editor, "file_path", None) == file_path:
                self.tabs.setCurrentIndex(i)
                return

        editor = CodeEditor()
        editor.file_path = file_path
        
        # Connect signals - Ideally these would be via a signal hub or dependency injection
        # But for now, we delegate back to main_window if it has the methods
        if hasattr(self.main_window, 'git_panel'):
            editor.git_blame_requested.connect(self.main_window.git_panel.show_blame)
            editor.git_history_requested.connect(self.main_window.git_panel.show_history)
        if hasattr(self.main_window, 'update_cursor_position'):
            editor.cursorPositionChanged.connect(self.main_window.update_cursor_position)

        try:
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    editor.setText(f.read())
                title = os.path.basename(file_path)
            else:
                title = "Untitled"
        except Exception as e:
            print(f"Failed to open {file_path}: {e}")
            return

        idx = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(idx)
        self.setup_tab_close_button(idx)

    def setup_tab_close_button(self, index):
        close_btn = QPushButton()
        close_btn.setIcon(load_icon("close.png", size=12))
        close_btn.setFixedSize(18, 18)
        close_btn.setStyleSheet("border: none; padding: 0; margin-left: 4px;")
        close_btn.clicked.connect(lambda _, i=index: self.close_tab(i))
        self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, close_btn)

    def save_current_file(self, save_as=False):
        editor = self.get_current_editor()
        if not editor:
            return

        file_path = getattr(editor, "file_path", None)

        if file_path and not save_as:
            self._write_file(file_path, editor)
        else:
            start_dir = self.main_window.project_path or os.getcwd()
            file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Save File", start_dir)
            if file_path:
                self._write_file(file_path, editor)
                editor.file_path = file_path
                idx = self.tabs.currentIndex()
                self.tabs.setTabText(idx, os.path.basename(file_path))
                
                if hasattr(self.main_window, '_update_last_open_folder'):
                    self.main_window._update_last_open_folder(os.path.dirname(file_path))

    def _write_file(self, path, editor):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.text())
            editor.setModified(False)
        except Exception as e:
            print(f"Error saving file: {e}")

    def save_all_files(self):
        count = self.tabs.count()
        for i in range(count):
            editor = self.tabs.widget(i)
            if hasattr(editor, "isModified") and editor.isModified():
                file_path = getattr(editor, "file_path", None)
                if file_path:
                    self._write_file(file_path, editor)

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if not editor:
            self.tabs.removeTab(index)
            return

        if hasattr(editor, "isModified") and editor.isModified():
            filename = os.path.basename(getattr(editor, "file_path", "Untitled") or "Untitled")
            reply = QMessageBox.question(
                self.main_window,
                "Unsaved Changes",
                f"Save changes to {filename}?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_current_file()

        self.tabs.removeTab(index)
        editor.deleteLater()
    
    def close_all_tabs(self):
        while self.tabs.count() > 0:
            self.close_tab(0)
