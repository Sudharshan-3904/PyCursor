"""
Shared Utility Functions for PyCursor IDE.
Provides helper methods for asset management, icon manipulation, 
and file system I/O specialized for development workflows.
"""

import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6 import QtSvg

def get_asset_path(*parts) -> str:
    """
    Returns the absolute path to an asset located in the project's assets directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.abspath(os.path.join(base_dir, "assets", *parts))

_ICON_CACHE = {}

def load_icon(name: str, size: int = 20, color: QColor = None) -> QIcon:
    """
    Loads and caches icons from the assets directory.
    Supports SVG/PNG format swapping and dynamic color tinting.
    """
    global _ICON_CACHE
    cache_key = (name, size, color.name() if color else None)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    icon_path = get_asset_path("icons", name)
    
    if not os.path.exists(icon_path):
        # Fallback to SVG/PNG swap
        alt_ext = ".svg" if name.endswith(".png") else ".png"
        alt_name = os.path.splitext(name)[0] + alt_ext
        icon_path = get_asset_path("icons", alt_name)
        
        if not os.path.exists(icon_path):
            basename = os.path.splitext(name)[0]
            icons_dir = get_asset_path("icons")
            found = False
            if os.path.exists(icons_dir):
                for f in os.listdir(icons_dir):
                    if f.startswith(basename):
                        icon_path = os.path.join(icons_dir, f)
                        found = True
                        break
            if not found:
                return QIcon()

    try:
        if icon_path.endswith(".svg"):
            renderer = QtSvg.QSvgRenderer(icon_path)
            pixmap = QPixmap(QSize(size * 2, size * 2))
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
        else:
            pixmap = QPixmap(icon_path).scaled(
                size * 2, size * 2,
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )

        if color:
            tinted_pixmap = QPixmap(pixmap.size())
            tinted_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(tinted_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.fillRect(tinted_pixmap.rect(), color)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            pixmap = tinted_pixmap

        icon = QIcon(pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        _ICON_CACHE[cache_key] = icon
        return icon
    except Exception:
        return QIcon()

def load_systemPrompt(filename: str = "generalPrompt.txt") -> str:
    """
    Retrieves the content of a system prompt text file used to guide AI behavior.
    """
    target_path = get_asset_path("systemPrompts", filename)

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError) as e:
        print(f"[Config Warning] Prompt template missing ({filename}): {e}")
        return "You are a professional coding assistant. Provide concise, accurate solutions."
