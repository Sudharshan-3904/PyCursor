from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QDateTime

class Terminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFixedHeight(150)
        self.setStyleSheet("background-color: #000; color: #00ff00;")
        self.append("PyCursor Terminal Ready\n")
    
    def log(self, message: str):
        """Logs a message with timestamp in the format 'timestamp |> message'"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.append(f"{timestamp} |> {message}")
