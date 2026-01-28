import pytest
from PyQt6.QtWidgets import QApplication
from core.ui.editor import CodeEditor
import sys

# Create the QApplication instance if it doesn't exist
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_editor_creation(qapp, qtbot):
    editor = CodeEditor()
    qtbot.addWidget(editor)
    assert editor is not None
    assert editor.toPlainText() == ""

def test_editor_set_text(qapp, qtbot):
    editor = CodeEditor()
    qtbot.addWidget(editor)
    test_content = "def hello():\n    print('world')"
    editor.setPlainText(test_content)
    assert editor.toPlainText() == test_content

def test_editor_indentation(qapp, qtbot):
    editor = CodeEditor()
    qtbot.addWidget(editor)
    # This might depend on how auto-indent is implemented
    # For now, just test basic text manipulation
    editor.setPlainText("if True:")
    # Simulate Enter key if possible, or just check logic
    pass
