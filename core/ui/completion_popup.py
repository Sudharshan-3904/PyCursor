from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor
from core.ui.theme import COLORS

class CompletionPopup(QFrame):
    """
    A custom, themed popup for IntelliSense completion suggestions.
    """
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 4px 8px;
                color: {COLORS['text_secondary']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['bg_selection']};
                color: {COLORS['accent_blue']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(16, 16))
        self.list_widget.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self.list_widget)
        
        self.setFixedSize(250, 200)

    def set_items(self, items: list):
        """
        Populate the list with completion items.
        Items should be a list of dicts: {"label": str, "kind": int}
        """
        self.list_widget.clear()
        for item in items:
            label = item.get("label", "")
            kind = item.get("kind", 1) # Default to Text
            
            list_item = QListWidgetItem(label)
            # Map LSP kind to icons (logic to be expanded)
            # list_item.setIcon(self._get_icon_for_kind(kind))
            self.list_widget.addItem(list_item)
        
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_item_activated(self, item):
        self.hide()
        # Callback logic to be handled by editor

    def show_at(self, pos):
        self.move(pos)
        self.show()
        self.list_widget.setFocus()
