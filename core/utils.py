import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter



# Utility to load icons
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