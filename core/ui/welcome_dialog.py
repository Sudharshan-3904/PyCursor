from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QWidget, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap
from core.ui.theme import COLORS
from core.utilities.utils import load_icon
import os

class WelcomeDialog(QDialog):
    """
    Onboarding/Welcome Dialog for PyCursor IDE.
    Shows features and tips to new users.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to PyCursor")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()

    def setup_ui(self):
        # Main container with rounded corners and border
        self.container = QFrame(self)
        self.container.setObjectName("WelcomeContainer")
        self.container.setFixedSize(700, 500)
        self.container.setStyleSheet(f"""
            #WelcomeContainer {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Section
        header = QFrame()
        header.setFixedHeight(150)
        header.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border-top-left-radius: 11px;
            border-top-right-radius: 11px;
            border-bottom: 1px solid {COLORS['border']};
        """)
        header_layout = QVBoxLayout(header)
        
        logo_label = QLabel()
        # Try to load a logo if exists, else text
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "logo.png")
        if os.path.exists(logo_path):
             pixmap = QPixmap(logo_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
             logo_label.setPixmap(pixmap)
        else:
             logo_label.setText("🚀")
             logo_label.setStyleSheet("font-size: 48px;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        title = QLabel("Welcome to PyCursor")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("The modern AI-powered IDE for Python developers")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)

        # Content Section (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: transparent;")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(20)

        features = [
            ("✨ AI-Powered Coding", "Smart completions, inline chat, and code explanation using local or API-based LLMs."),
            ("📁 Project Management", "Easily manage environments, dependencies, and git repositories."),
            ("🎨 Modern Interface", "Focused on productivity with a beautiful Catppuccin-inspired dark theme."),
            ("⚙️ Highly Customizable", "Personalize shortcuts, themes, and extensions to fit your workflow.")
        ]

        for title_text, desc_text in features:
            feature_item = QWidget()
            f_layout = QVBoxLayout(feature_item)
            f_layout.setContentsMargins(0, 0, 0, 0)
            f_layout.setSpacing(5)
            
            f_title = QLabel(title_text)
            f_title.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 16px; font-weight: bold;")
            f_desc = QLabel(desc_text)
            f_desc.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px;")
            f_desc.setWordWrap(True)
            
            f_layout.addWidget(f_title)
            f_layout.addWidget(f_desc)
            content_layout.addWidget(feature_item)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Footer Section
        footer = QFrame()
        footer.setFixedHeight(70)
        footer.setStyleSheet(f"border-top: 1px solid {COLORS['border']};")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        
        version_label = QLabel("Version 0.2.0")
        version_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        footer_layout.addWidget(version_label)
        
        footer_layout.addStretch()
        
        start_btn = QPushButton("Get Started")
        start_btn.setFixedSize(120, 36)
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: white;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_blue_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_tertiary']};
            }}
        """)
        start_btn.clicked.connect(self.accept)
        footer_layout.addWidget(start_btn)
        
        layout.addWidget(footer)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
