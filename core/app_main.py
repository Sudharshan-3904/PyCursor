# app_main.py
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QTabWidget,
    QWidget, QVBoxLayout, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from core.utils import load_icon
from core.ui.sidebar import SideBar
from core.ui.editor import CodeEditor
from core.ui.terminal import Terminal
from core.ai.ai_engine import AIAssistantWidget  # AI widget



class PyCursorMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCursor IDE")
        self.resize(1200, 800)

        # --- Center Editor Tabs ---
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.setCentralWidget(self.editor_tabs)

        # --- Left Dock: Explorer ---
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

        # --- Right Dock: AI Assistant ---
        self.ai_widget = AIAssistantWidget()
        self.ai_dock = QDockWidget("AI Assistant", self)
        self.ai_dock.setWidget(self.ai_widget)
        self.ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.ai_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)

        # --- Bottom Dock: Terminal Tabs ---
        self.terminal_tabs = QTabWidget()
        self.add_terminal_tab("Terminal 1")  # Start with one terminal

        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setWidget(self.terminal_tabs)
        self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.terminal_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        # --- Menu Bar ---
        self.create_menu_bar()

    # --- Menu Bar ---
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file_dialog)
        save_action = QAction("Save File", self)
        save_action.triggered.connect(self.save_file)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

    # --- Open File Dialog ---
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*)")
        if file_path:
            self.open_file_in_tab(file_path)

    # --- Save File ---
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
                file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*.*)")
                if file_path:
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(editor.toPlainText())
                        editor.file_path = file_path
                        self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), os.path.basename(file_path))
                    except Exception as e:
                        print(f"Failed to save {file_path}: {e}")

    # --- Open file in editor tab ---
    def open_file_in_tab(self, file_path: str):
        # Check if already open
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

        self.editor_tabs.addTab(editor, os.path.basename(file_path))
        self.editor_tabs.setCurrentWidget(editor)

    # --- Close editor tab ---
    def close_editor_tab(self, index):
        widget = self.editor_tabs.widget(index)
        self.editor_tabs.removeTab(index)
        widget.deleteLater()

    # --- Add terminal tab ---
    def add_terminal_tab(self, name="Terminal"):
        term = Terminal()
        self.terminal_tabs.addTab(term, name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
