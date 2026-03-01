import os
from PyQt6.QtWidgets import QTabWidget, QMessageBox, QFileDialog, QPushButton, QTabBar, QApplication, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from core.ui.editor import CodeEditor
from core.utilities.utils import load_icon

class EditorManager:
    """
    Controller class responsible for managing the central editor area.
    Handles tab creation, file I/O operations, and document state management.
    """
    def __init__(self, main_window, tab_widget: QTabWidget):
        """
        Initializes the manager with a reference to the main window and its tab container.
        """
        self.main_window = main_window
        self.tabs = tab_widget
        self._setup_tabs()

    def _setup_tabs(self):
        """
        Configures the QTabWidget behavior (closable, movable, custom context menus).
        """
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)

    def _on_tab_changed(self, index):
        """
        Internal handler to update UI components (like status bar) when active editor changes.
        """
        if hasattr(self.main_window, 'update_status_bar'):
            self.main_window.update_status_bar()

    def get_current_editor(self) -> CodeEditor:
        """
        Returns the currently active CodeEditor instance, or None if no tabs are open.
        """
        editor = self.tabs.currentWidget()
        return editor if isinstance(editor, CodeEditor) else None

    def open_file(self, file_path: str):
        """
        Opens a file in a new tab or switches to it if already open.
        Includes performance checks for large files.
        """
        # Check for already open documents
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if getattr(editor, "file_path", None) == file_path:
                self.tabs.setCurrentIndex(i)
                return

        editor = CodeEditor()
        editor.file_path = file_path
        
        # Apply the current theme immediately
        if hasattr(self.main_window, '_settings'):
            current_theme = self.main_window._settings.get("theme", "dark")
            editor.apply_theme_colors(current_theme)
        
        # Connect editor-specific signals to main window handlers
        if hasattr(self.main_window, 'git_panel'):
            editor.git_blame_requested.connect(self.main_window.git_panel.show_blame)
            editor.git_history_requested.connect(self.main_window.git_panel.show_history)
        if hasattr(self.main_window, 'update_cursor_position'):
            editor.cursorPositionChanged.connect(self.main_window.update_cursor_position)

        try:
            if file_path:
                # Security/Performance check for large files (>5MB)
                file_size = os.path.getsize(file_path)
                if file_size > 5 * 1024 * 1024:
                    confirm = QMessageBox.warning(
                        self.main_window, "Large File",
                        f"Opening '{os.path.basename(file_path)}' ({file_size/1e6:.1f}MB) may be slow. Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if confirm == QMessageBox.StandardButton.No: return

                with open(file_path, "r", encoding="utf-8") as f:
                    editor.setText(f.read())
                title = os.path.basename(file_path)
                editor.setModified(False)
            else:
                title = "Untitled"
        except Exception as e:
            print(f"I/O Error opening {file_path}: {e}")
            return

        idx = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(idx)

    def save_current_file(self, save_as=False):
        """
        Saves the content of the active editor tab.
        """
        editor = self.get_current_editor()
        if not editor: return

        file_path = getattr(editor, "file_path", None)

        if file_path and not save_as:
            self._write_to_disk(file_path, editor)
        else:
            path, _ = QFileDialog.getSaveFileName(self.main_window, "Save File As", self.main_window.project_path)
            if path:
                self._write_to_disk(path, editor)
                editor.file_path = path
                self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))

    def _write_to_disk(self, path, editor):
        """
        Internal utility for physical file write operations.
        Updates the AI RAG index after successful save.
        """
        try:
            content = editor.text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            editor.setModified(False)
            
            # Update RAG Index
            if hasattr(self.main_window, 'ai_widget'):
                rag = self.main_window.ai_widget.context_manager.rag_manager
                if rag:
                    rag.add_documents(path, content)
        except Exception as e:
            print(f"Error persisting file: {e}")

    def save_all_files(self):
        """
        Iterates through all tabs and saves documents with pending modifications.
        """
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if hasattr(editor, "isModified") and editor.isModified():
                path = getattr(editor, "file_path", None)
                if path: self._write_to_disk(path, editor)

    def close_tab(self, index):
        """
        Closes a specific tab, prompting for save if modifications exist.
        """
        editor = self.tabs.widget(index)
        if not editor:
            self.tabs.removeTab(index)
            return

        if hasattr(editor, "isModified") and editor.isModified():
            filename = os.path.basename(getattr(editor, "file_path", "Untitled") or "Untitled")
            reply = QMessageBox.question(
                self.main_window, "Save Changes?",
                f"'{filename}' has unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel: return
            if reply == QMessageBox.StandardButton.Yes: self.save_current_file()

        self.tabs.removeTab(index)
        editor.deleteLater()
    
    def close_all_tabs(self):
        """
        Closes all open editor tabs.
        """
        while self.tabs.count() > 0:
            self.close_tab(0)

    def show_tab_context_menu(self, position):
        """
        Displays management actions (Close Others, Copy Path) for tab handles.
        """
        index = self.tabs.tabBar().tabAt(position)
        menu = QMenu()
        
        if index >= 0:
            menu.addAction("Close", lambda: self.close_tab(index))
            menu.addAction("Close Others", lambda: self.close_others(index))
            menu.addAction("Close to the Right", lambda: self.close_to_right(index))
            menu.addSeparator()
            
            editor = self.tabs.widget(index)
            if editor and hasattr(editor, 'file_path'):
                path_act = QAction("Copy Full Path", self.main_window)
                path_act.triggered.connect(lambda: QApplication.clipboard().setText(editor.file_path))
                menu.addAction(path_act)
        else:
            menu.addAction("Close All Tabs", self.close_all_tabs)
            
        menu.exec(self.tabs.mapToGlobal(position))

    def close_others(self, index):
        """
        Closes all tabs except the one at the specified index.
        """
        for i in range(self.tabs.count() - 1, index, -1): self.close_tab(i)
        for i in range(index - 1, -1, -1): self.close_tab(i)

    def close_to_right(self, index):
        """
        Closes all tabs to the right of the specified index.
        """
        for i in range(self.tabs.count() - 1, index, -1): self.close_tab(i)
