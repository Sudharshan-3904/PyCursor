"""
Git Dialogs for PyCursor IDE

Dialogs for Git Blame and History.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from core.ui.theme import COLORS
from datetime import datetime


class GitBlameDialog(QDialog):
    """Dialog to show Git blame information"""
    
    def __init__(self, file_path: str, blame_data: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Git Blame - {file_path}")
        self.resize(800, 600)
        self.blame_data = blame_data
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Line", "Commit", "Author", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                padding: 4px;
                border: 1px solid {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
        """)
        
        self.populate_table()
        layout.addWidget(self.table)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
    def populate_table(self):
        self.table.setRowCount(len(self.blame_data))
        
        for row, data in enumerate(self.blame_data):
            # Line number (row + 1)
            line_item = QTableWidgetItem(str(row + 1))
            line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, line_item)
            
            commit_item = QTableWidgetItem(data['commit'])
            self.table.setItem(row, 1, commit_item)
            
            author_item = QTableWidgetItem(data['author'])
            self.table.setItem(row, 2, author_item)
            
            date_str = data['date'].strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 3, date_item)


class GitHistoryDialog(QDialog):
    """Dialog to show Git file history"""
    
    def __init__(self, file_path: str, history_data: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Git History - {file_path}")
        self.resize(800, 600)
        self.history_data = history_data
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Commit", "Author", "Date", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                padding: 4px;
                border: 1px solid {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
        """)
        
        self.populate_table()
        layout.addWidget(self.table)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
    def populate_table(self):
        self.table.setRowCount(len(self.history_data))
        
        for row, commit in enumerate(self.history_data):
            commit_item = QTableWidgetItem(commit.short_sha)
            self.table.setItem(row, 0, commit_item)
            
            author_item = QTableWidgetItem(commit.author)
            self.table.setItem(row, 1, author_item)
            
            date_str = commit.date.strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 2, date_item)
            
            msg_item = QTableWidgetItem(commit.message)
            self.table.setItem(row, 3, msg_item)
