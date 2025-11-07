import os
import sys
import platform
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtWidgets import QTextEditb
from PyQt6.QtGui import QTextCursor

# TODO - Make terminal resizeable
class Terminal(QTextEdit):
    def __init__(self, project_path=None):
        super().__init__()
        self.setReadOnly(False)
        self.setAcceptRichText(False)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 5px;
            }
        """)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setUndoRedoEnabled(False)

        self.project_path = project_path or os.getcwd()
        self.shell = self._detect_shell()
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_output)
        self.process.readyReadStandardError.connect(self._on_output)

        # Prepare environment variables
        env = os.environ.copy()
        activate_cmd = self._get_env_activation_path()
        if activate_cmd and os.path.exists(activate_cmd):
            if platform.system() != "Windows":
                # Prepend venv/bin to PATH
                env["PATH"] = os.path.join(activate_cmd, "..") + os.pathsep + env["PATH"]
            else:
                env["PATH"] = os.path.join(activate_cmd, "..") + os.pathsep + env["PATH"]

        self.process.setProcessEnvironment(env)

        # Start shell
        self.process.start(self.shell)
        self.prompt = f"{os.getcwd()} $ " if os.name != "nt" else f"{os.getcwd()}> "
        self.append(self.prompt)

    # ─────────────────────────────────────────────
    def _detect_shell(self):
        """Detect system shell (bash/zsh/cmd/powershell)."""
        if platform.system() == "Windows":
            return os.environ.get("COMSPEC", "cmd.exe")
        elif platform.system() == "Darwin":
            return os.environ.get("SHELL", "/bin/zsh")
        else:
            return os.environ.get("SHELL", "/bin/bash")

    # ─────────────────────────────────────────────
    def _get_env_activation_path(self):
        """Return path to venv's activate script."""
        venv_path = os.path.join(self.project_path, "venv")
        if os.path.exists(venv_path):
            if platform.system() == "Windows":
                return os.path.join(venv_path, "Scripts", "python.exe")
            else:
                return os.path.join(venv_path, "bin", "python")
        return None

    # ─────────────────────────────────────────────
    def _on_output(self):
        """Append output from shell."""
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        if data:
            self.moveCursor(QTextCursor.MoveOperation.End)
            self.insertPlainText(data)
            self.ensureCursorVisible()

    # ─────────────────────────────────────────────
    def keyPressEvent(self, event):
        """Send input to shell."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Get last line
            text = self.toPlainText().split("\n")[-1].replace(self.prompt, "")
            if text.strip():
                self.process.write((text.strip() + "\n").encode("utf-8"))
            self.append("")  # new line
            return

        # Prevent deleting the prompt
        elif event.key() == Qt.Key.Key_Backspace:
            line = self.toPlainText().split("\n")[-1]
            if len(line) <= len(self.prompt):
                return

        super().keyPressEvent(event)
