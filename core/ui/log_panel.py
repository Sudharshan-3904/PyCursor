from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
from core.ui.theme import COLORS

class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                border: none;
                font-family: Consolas, monospace;
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.log_area)

    def log(self, message: str):
        self.log_area.append(message)
        # Auto-scroll
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
