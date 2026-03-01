
import sys
import os
from PyQt6.QtWidgets import QApplication, QTabWidget, QMainWindow

# Add project root to path
sys.path.append(r"e:\Tester\PyCursor")

from core.ide.editor_manager import EditorManager

app = QApplication(sys.argv)
win = QMainWindow()
tabs = QTabWidget()
win.setCentralWidget(tabs)

manager = EditorManager(win, tabs)
print("EditorManager created")

# Try to open this very file
file_to_open = __file__
try:
    manager.open_file(file_to_open)
    print(f"Successfully opened {file_to_open}")
    editor = manager.get_current_editor()
    if editor:
        print(f"Editor text length: {len(editor.text())}")
        # Test cursor_pos_to_pixel
        pos = editor.cursor_pos_to_pixel()
        print(f"Cursor position: {pos.x()}, {pos.y()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Success!")
