import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QWidget,
    QVBoxLayout, QFileDialog, QTabWidget, QPushButton, QTabBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction,  QIcon, QPixmap, QPainter
import os

from core.ui.sidebar import SideBar
from core.ui.editor import CodeEditor
from core.ui.terminal import Terminal


def load_icon(name: str, size=20, recolor_to_white=True) -> QIcon:
    base_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")
    icon_path = os.path.abspath(os.path.join(base_dir, name))
    if not os.path.exists(icon_path):
        print(f"[Icon Warning] Missing icon file: {icon_path}")
        return QIcon()

    pixmap = QPixmap(icon_path).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    if recolor_to_white:
        white_pixmap = QPixmap(pixmap.size())
        white_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(white_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(white_pixmap.rect(), Qt.GlobalColor.white)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return QIcon(white_pixmap)

    return QIcon(pixmap)


def set_custom_tab_close_icons(tab_widget: QTabWidget, icon_name: str, size=16):
    """Set a custom close icon for all tabs in a QTabWidget."""
    tab_widget.setTabsClosable(True)
    close_icon = load_icon(icon_name, size=size)

    for i in range(tab_widget.count()):
        # Create a QPushButton for the close button
        close_btn = QPushButton()
        close_btn.setIcon(close_icon)
        close_btn.setIconSize(QSize(size, size))
        close_btn.setFixedSize(size + 4, size + 4)  # Add a little padding
        close_btn.setStyleSheet(
            """
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: #ff5555;
            }
            """
        )
        close_btn.clicked.connect(lambda _, index=i: tab_widget.removeTab(index))
        tab_widget.setTabButton(i, QTabWidget.TabPosition.RightSide, close_btn)


class PyCursorMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCursor IDE")
        self.resize(1200, 800)

        # --- Core Widgets ---
        self.sidebar = SideBar()  # project file tree
        self.terminal = Terminal()  # logging / console
        self.tab_widget = QTabWidget()  # multi-tab editor
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Connect sidebar click signal
        self.sidebar.file_selected.connect(self.open_file_in_tab)

        # --- Layout ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.terminal)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

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

    # --- File Dialog Open ---
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*)")
        if file_path:
            self.open_file_in_tab(file_path)

    # --- Save Current Tab ---
    def save_file(self):
        editor = self.tab_widget.currentWidget()
        if editor:
            if hasattr(editor, "file_path") and editor.file_path:
                # Save to existing path
                try:
                    with open(editor.file_path, "w", encoding="utf-8") as f:
                        f.write(editor.toPlainText())
                    self.terminal.log(f"Saved {editor.file_path}")
                except Exception as e:
                    self.terminal.log(f"Failed to save {editor.file_path}: {e}")
            else:
                # Save as new file
                file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*.*)")
                if file_path:
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(editor.toPlainText())
                        editor.file_path = file_path
                        self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split("/")[-1])
                        self.terminal.log(f"Saved {file_path}")
                    except Exception as e:
                        self.terminal.log(f"Failed to save {file_path}: {e}")

    # --- Open file in tab ---
    def open_file_in_tab(self, file_path: str):
        """Open a file in a new tab or switch if already open."""
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if getattr(editor, "file_path", None) == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        editor = CodeEditor()
        editor.file_path = file_path

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                editor.setText(f.read())
        except Exception as e:
            self.terminal.log(f"Failed to open {file_path}: {e}")
            return

        file_name = file_path.split("/")[-1]
        index = self.tab_widget.addTab(editor, file_name)
        self.tab_widget.setCurrentIndex(index)

        close_icon = load_icon("close.png", size=16)
        close_btn = QPushButton()
        close_btn.setIcon(close_icon)
        close_btn.setIconSize(QSize(16,16))
        close_btn.setFixedSize(20,20)
        close_btn.setStyleSheet(
            """
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: #ff5555;
            }
            """
        )
        close_btn.clicked.connect(lambda _, i=index: self.tab_widget.removeTab(i))
        # self.tab_widget.setTabButton(index, QTabWidget.TabPosition.RightSide, close_btn)
        self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, close_btn)

        self.terminal.log(f"Opened {file_path}")


    # --- Close tab ---
    def close_tab(self, index: int):
        editor = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        editor.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyCursorMain()
    win.show()
    sys.exit(app.exec())
