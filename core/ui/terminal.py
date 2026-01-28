import os
import platform
from PyQt6.QtCore import QProcess, QProcessEnvironment, Qt
from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from PyQt6.QtGui import QTextCursor
from core.ui.theme import COLORS

class Terminal(QTextEdit):
    """
    Integrated shell terminal emulator for executing system commands.
    Combines a QTextEdit for display with a QProcess for persistent shell interaction.
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
            shell_args = ["-i"] # Interactive mode

        self.process.start(self.shell, shell_args)
        if not self.process.waitForStarted(3000):
            self.append("[Terminal] Fatal: Failed to initialize shell process.")

        self.prompt = f"{self.project_path} $ " if os.name != "nt" else f"{self.project_path}> "
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        self.append(self.prompt)

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
        if data:
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
            
            # Extract actual command text by stripping prompt
            for sep in (">", "$", ":"):
                idx = cmd.rfind(sep)
                if idx != -1:
                    cmd = cmd[idx + 1:].strip()
                    break

            # Handle internal controls (clear)
            if cmd.lower() in ("cls", "clear"):
                self.clear()
                self.append(self.prompt)
                return

            # Submit command to background process
            if cmd:
                newline = "\r\n" if platform.system() == "Windows" else "\n"
                self.process.write((cmd + newline).encode("utf-8"))
            self.append("")
            return

        elif event.key() == Qt.Key.Key_Backspace:
            # Prevent backspacing through the shell prompt
            line = self.toPlainText().split("\n")[-1]
            if len(line) <= len(self.prompt):
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
        self.prompt = f"{self.project_path} $ " if os.name != "nt" else f"{self.project_path}> "
        
        if self.process.state() == QProcess.ProcessState.Running:
            cd_cmd = f"cd \"{new_path}\"" if os.name == "nt" else f"cd '{new_path}'"
            self.execute_command(cd_cmd)
