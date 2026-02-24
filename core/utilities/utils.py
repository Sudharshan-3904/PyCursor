"""
Shared Utility Functions for PyCursor IDE.
Provides helper methods for asset management, icon manipulation, 
and file system I/O specialized for development workflows.
"""

import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor

def load_icon(name: str, size: int = 20, color: QColor = None) -> QIcon:
    """
    Loads an SVG or PNG icon from the assets directory and optionally applies 
    a color transformation to match the application's theme aesthetics.
    """
    # Resolve absolute path to the icon asset
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")
    icon_path = os.path.abspath(os.path.join(base_dir, name))
    
    if not os.path.exists(icon_path):
        # Fallback to SVG if PNG doesn't exist or vice versa
        alt_name = name.replace(".png", ".svg") if name.endswith(".png") else name.replace(".svg", ".png")
        icon_path = os.path.abspath(os.path.join(base_dir, alt_name))
        
        if not os.path.exists(icon_path):
            print(f"[UI Warning] Asset not found: {name}")
            return QIcon()

    # Load and scale the pixmap for high-DPI awareness
    pixmap = QPixmap(icon_path).scaled(
        size * 2, size * 2, # Scale for better quality before tinting
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    )

    # Apply tinting
    if color:
        tinted_pixmap = QPixmap(pixmap.size())
        tinted_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(tinted_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(tinted_pixmap.rect(), color)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return QIcon(tinted_pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    return QIcon(pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

def load_systemPrompt(filename: str = "generalPrompt.txt") -> str:
    """
    Retrieves the content of a system prompt text file used to guide AI behavior.
    """
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    target_path = os.path.join(root, "assets", "systemPrompts", filename)

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError) as e:
        print(f"[Config Warning] Prompt template missing ({filename}): {e}")
        # Return a conservative fallback prompt to ensure the AI engine remains functional
        return "You are a professional coding assistant. Provide concise, accurate solutions."
