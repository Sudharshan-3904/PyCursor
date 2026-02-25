import os
import platform
from PyQt6.QtCore import QProcess, QProcessEnvironment, Qt
from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from PyQt6.QtGui import QTextCursor, QFont, QFontDatabase, QFontInfo
from core.ui.theme import COLORS

class Terminal(QTextEdit):
    """
    Integrated shell terminal emulator for executing system commands.
    Combines a QTextEdit for display with a QProcess for persistent shell interaction.

    This simplified implementation **does not append a custom prompt**; instead
    it allows the underlying shell to render its own prompt.  That avoids the
    duplicated-directory problem entirely and keeps output identical to a normal
    terminal session.  The prompt-related logic is retained only for command
    extraction and backspace protection, which are heuristic and tolerant of
    whatever the shell chooses to show.
    """

    def __init__(self, project_path=None):
        """
        Initializes the terminal and starts the underlying system shell process.
        """
        super().__init__()
        self.setReadOnly(False)
        self.setAcceptRichText(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(100)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setUndoRedoEnabled(False)

        # Set font to prevent invalid font sizes
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            font = QFont("Courier New", 10)
            font.setPointSize(10)
        self.setFont(font)

        self.project_path = project_path or os.getcwd()
        self.shell = self._detect_shell()

        # Configure the persistent shell process
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_output)
        self.process.readyReadStandardError.connect(self._on_output)

        if os.path.isdir(self.project_path):
            self.process.setWorkingDirectory(self.project_path)

        # Inherit and augment system environment variables
        env = QProcessEnvironment.systemEnvironment()
        for key, value in os.environ.items():
            env.insert(str(key), str(value))

        # Attempt to auto-inject project virtual environment into PATH
        python_exec = self._get_env_activation_path()
        if python_exec:
            venv_bin_dir = os.path.dirname(python_exec)
            env.insert("PATH", venv_bin_dir + os.pathsep + env.value("PATH"))

        self.process.setProcessEnvironment(env)

        # Start shell with appropriate platform flags
        shell_args = []
        if platform.system() == "Windows":
            shell_args = ["-NoExit"] if "powershell" in self.shell.lower() or "pwsh" in self.shell.lower() else ["/K"]
        else:
            shell_args = ["-i"]  # Interactive mode

        self.process.start(self.shell, shell_args)
        if not self.process.waitForStarted(3000):
            self.append("[Terminal] Fatal: Failed to initialize shell process.")

        # placeholder used for legacy code; kept empty
        self.prompt = ""
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def __del__(self):
        """
        Properly terminates the shell process when the terminal is destroyed.
        """
        if hasattr(self, 'process') and self.process:
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.terminate()
                if not self.process.waitForFinished(3000):
                    self.process.kill()

    def _detect_shell(self):
        """
        Determines the default system shell based on the current operating system.
        """
        if platform.system() == "Windows":
            return os.environ.get("COMSPEC", "cmd.exe")
        return os.environ.get("SHELL", "/bin/bash")

    def _get_env_activation_path(self):
        """
        Locates the project-specific virtual environment executable if it exists.
        """
        venv_path = os.path.join(self.project_path, "venv")
        if os.path.exists(venv_path):
            if platform.system() == "Windows":
                return os.path.join(venv_path, "Scripts", "python.exe")
            return os.path.join(venv_path, "bin", "python")
        return None

    def _on_output(self):
        """
        Asynchronously streams output from the shell process to the terminal display.
        """
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        if not data:
            return

        # simply forward everything the shell emits; we no longer try to filter
        # out startup echoes.  By not appending our own prompt in __init__, we
        # avoid duplicating whatever the shell prints.
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertPlainText(data)
        self.ensureCursorVisible()

    def keyPressEvent(self, event):
        """
        Handles user input from the keyboard, intercepting Enter and Backspace
        to manage command submission and prompt protection.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            last_line = self.toPlainText().split("\n")[-1]
            cmd = last_line.strip()

            # Extract actual command text by stripping anything up to the last
            # (typically shell) prompt separator.  This heuristic works with
            # "path> ", ":~$ ", etc.
            for sep in (">", "$", ":"):
                idx = cmd.rfind(sep)
                if idx != -1:
                    cmd = cmd[idx + 1:].strip()
                    break

            # Handle internal controls (clear)
            if cmd.lower() in ("cls", "clear"):
                self.clear()
                return

            # Submit command to background process
            if cmd:
                newline = "\r\n" if platform.system() == "Windows" else "\n"
                self.process.write((cmd + newline).encode("utf-8"))
            self.append("")
            return

        elif event.key() == Qt.Key.Key_Backspace:
            # simple backspace protection: don't delete when the current line is
            # already empty (avoids erasing previous output when cursor is at
            # start of line)
            line = self.toPlainText().split("\n")[-1]
            if len(line) <= 0:
                return

        super().keyPressEvent(event)

    def execute_command(self, command: str):
        """
        Programmatically injects and executes a command into the running shell.
        """
        if self.process.state() != QProcess.ProcessState.Running:
            return

        self.moveCursor(QTextCursor.MoveOperation.End)
        self.append(f"\n--- [Executing: {command}] ---\n")
        self.process.write((command + "\n").encode("utf-8"))
        self.ensureCursorVisible()

    def set_project_path(self, new_path: str):
        """
        Updates the working directory of the terminal environment.
        """
        if not os.path.isdir(new_path):
            return

        self.project_path = new_path
        # we no longer maintain a custom prompt value
        if self.process.state() == QProcess.ProcessState.Running:
            cd_cmd = f"cd \"{new_path}\"" if os.name == "nt" else f"cd '{new_path}'"
            self.execute_command(cd_cmd)
