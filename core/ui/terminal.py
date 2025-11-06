import os
import sys
import platform
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtGui import QTextCursor


class Terminal(QTextEdit):
    def __init__(self):
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

        self.shell = self._detect_shell()
        self.process = QProcess(self)
        self._init_process()

        self.prompt = f"{os.getcwd()} $ " if os.name != "nt" else f"{os.getcwd()}> "
        self.append(self.prompt)
        self.cursor = self.textCursor()

    # ─────────────────────────────────────────────
    # Initialize QProcess for the shell
    def _init_process(self):
        """Start shell process and connect signals."""
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_output)
        self.process.readyReadStandardError.connect(self._on_output)
        self.process.start(self.shell)

    def _detect_shell(self):
        """Detects system shell (bash/zsh/cmd/powershell)."""
        if platform.system() == "Windows":
            return os.environ.get("COMSPEC", "cmd.exe")
        elif platform.system() == "Darwin":
            return os.environ.get("SHELL", "/bin/zsh")
        else:
            return os.environ.get("SHELL", "/bin/bash")

    # ─────────────────────────────────────────────
    # Output handling
    def _on_output(self):
        """Read output from shell and append to terminal."""
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        if data:
            self.moveCursor(QTextCursor.MoveOperation.End)
            self.insertPlainText(data)
            self.ensureCursorVisible()

    def keyPressEvent(self, event):
        """Handle user key presses."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

            text = self.toPlainText().split("\n")[-1].replace(self.prompt, "").strip()
            if text:
                self.process.write((text + "\n").encode("utf-8"))
            self.append("")  # new line after command
            return


        # ─────────────────────────────────────────────
        # Helper: reset prompt after each command
        def append_prompt(self):
            """Append the shell prompt after output."""
            self.append(self.prompt)
            self.moveCursor(QTextCursor.End)
            self.ensureCursorVisible()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.setFixedHeight(250)
    terminal.show()
    sys.exit(app.exec())

