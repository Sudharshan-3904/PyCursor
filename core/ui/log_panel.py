"""
Log Panel Module

This module implements a centralized logging widget for the application.
It provides a read-only text area to display system messages, errors, and status updates,
keeping them separate from the primary AI chat interface.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase, QFontInfo
from core.ui.theme import COLORS

class LogPanel(QWidget):
    """
    A widget acting as a system console for application logs.
    
    Displays chronological log messages with auto-scrolling capabilities.
    Designed to sit in the sidebar stack.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        # Set font to prevent invalid font sizes
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            font = QFont("Courier New", 11)
            font.setPointSize(11)
        self.log_area.setFont(font)
        
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                border: none;
            }}
        """)
        layout.addWidget(self.log_area)

    def log(self, message: str):
        self.log_area.append(message)
        # Auto-scroll
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
