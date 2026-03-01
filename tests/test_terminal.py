import pytest
from core.ui.terminal import Terminal
from PyQt6.QtWidgets import QApplication
import sys
from PyQt6.QtCore import QByteArray, QProcess


class FakeProcess:
    def __init__(self, text):
        self._text = text
    def readAllStandardOutput(self):
        return QByteArray(self._text.encode('utf-8'))


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_no_custom_prompt(qapp, qtbot, tmp_path):
    """After initialization, the terminal should not have injected its own prompt."""
    term = Terminal(project_path=str(tmp_path))
    qtbot.addWidget(term)
    assert term.prompt == ""


def test_output_forwarded(qapp, qtbot, tmp_path):
    term = Terminal(project_path=str(tmp_path))
    qtbot.addWidget(term)
    # fake process output should appear verbatim
    term.process = FakeProcess("abc123\n")
    term.clear()
    term._on_output()
    assert term.toPlainText() == "abc123\n"


def test_enter_submits_command(qapp, qtbot, tmp_path):
    """Typing a command and pressing Enter should write it to the process."""
    term = Terminal(project_path=str(tmp_path))
    qtbot.addWidget(term)

    class Recorder:
        def __init__(self):
            self.written = b""
            self._state = QProcess.ProcessState.Running
        def state(self):
            return self._state
        def write(self, data):
            self.written += data

    recorder = Recorder()
    term.process = recorder

    # simulate a shell prompt and user typing 'echo hi'
    term.setText(f"{tmp_path}> echo hi")
    # create a key event for Enter
    from PyQt6.QtGui import QKeyEvent
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    term.keyPressEvent(event)

    # our recorder should have received the command plus newline
    assert recorder.written.endswith(b"echo hi\n")


# previous suppression tests removed; behaviour simplified
