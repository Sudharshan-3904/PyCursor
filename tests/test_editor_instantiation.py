
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(r"e:\Tester\PyCursor")

try:
    from core.ui.editor import CodeEditor
    print("CodeEditor imported successfully")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = QApplication(sys.argv)
try:
    editor = CodeEditor()
    print("CodeEditor instantiated successfully")
except Exception as e:
    print(f"Instantiation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Success!")
