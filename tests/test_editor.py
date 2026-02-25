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
    # QsciScintilla uses text()/setText(), not Qt's toPlainText
    assert editor.text() == ""

def test_editor_set_text(qapp, qtbot):
    editor = CodeEditor()
    qtbot.addWidget(editor)
    test_content = "def hello():\n    print('world')"
    editor.setText(test_content)
    assert editor.text() == test_content

def test_editor_indentation(qapp, qtbot):
    editor = CodeEditor()
    qtbot.addWidget(editor)
    # This might depend on how auto-indent is implemented
    # For now, just test basic text manipulation
    editor.setText("if True:")
    # Simulate Enter key if possible, or just check logic
    pass


def test_completion_insertion(qapp, qtbot):
    """Verify that selecting a completion item inserts/replaces text correctly."""
    editor = CodeEditor()
    qtbot.addWidget(editor)
    # simulate partially typed identifier
    editor.setText("pri")
    editor.setCursorPosition(0, 3)
    from PyQt6.QtWidgets import QListWidgetItem
    item = QListWidgetItem("print")
    editor._on_completion_selected(item)
    # after insertion 'pri' should be replaced by 'print'
    assert editor.text().startswith("print")
