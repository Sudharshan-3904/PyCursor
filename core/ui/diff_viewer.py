"""
Diff Viewer Dialog for PyCursor IDE

Visual diff viewer for Git changes.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
from core.ui.theme import COLORS


class DiffViewer(QDialog):
    """Dialog for viewing file diffs"""
    
    def __init__(self, file_path: str, diff_text: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.diff_text = diff_text
        
        self.setWindowTitle(f"Diff - {file_path}")
        self.resize(800, 600)
        
        self.init_ui()
        self.display_diff()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # Header
        header = QLabel(f"Changes in: {self.file_path}")
        header.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        layout.addWidget(header)
        
        # Diff display
        self.diff_display = QTextEdit()
        self.diff_display.setReadOnly(True)
        self.diff_display.setFont(QFont("Consolas", 10))
        self.diff_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['editor_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.diff_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def display_diff(self):
        """Display the diff with syntax highlighting"""
        if not self.diff_text:
            self.diff_display.setPlainText("No changes")
            return
        
        # Parse and color the diff
        lines = self.diff_text.split('\n')
        html_lines = []
        
        for line in lines:
            if line.startswith('+++') or line.startswith('---'):
                # File headers
                html_lines.append(f'<span style="color: {COLORS["text_secondary"]}; font-weight: bold;">{self.escape_html(line)}</span>')
            elif line.startswith('+'):
                # Added lines
                html_lines.append(f'<span style="background-color: #1a4d1a; color: #4ec9b0;">{self.escape_html(line)}</span>')
            elif line.startswith('-'):
                # Removed lines
                html_lines.append(f'<span style="background-color: #4d1a1a; color: #f48771;">{self.escape_html(line)}</span>')
            elif line.startswith('@@'):
                # Hunk headers
                html_lines.append(f'<span style="color: {COLORS["accent_blue"]}; font-weight: bold;">{self.escape_html(line)}</span>')
            else:
                # Context lines
                html_lines.append(f'<span style="color: {COLORS["text_primary"]};">{self.escape_html(line)}</span>')
        
        html = '<pre style="margin: 0; padding: 8px;">' + '<br>'.join(html_lines) + '</pre>'
        self.diff_display.setHtml(html)
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
