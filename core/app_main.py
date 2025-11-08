import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTabWidget, QFileDialog, QMessageBox, QTabBar, QPushButton
from PyQt6.QtCore import Qt
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

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.setCentralWidget(self.editor_tabs)
        self.editor_tabs.setStyleSheet("""
            QTabBar::close-button {
                image: url(close.png);
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
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
        self.ai_dock = QDockWidget("AI Assistant", self)
        self.ai_dock.setWidget(self.ai_widget)
        self.ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.ai_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)

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
        save_action = QAction("Save File", self)
        save_action.triggered.connect(self.save_file)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*)")
        if file_path:
            self.open_file_in_tab(file_path)

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

    def add_terminal_tab(self, name="Terminal"):
        term = Terminal()
        self.terminal_tabs.addTab(term, name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
