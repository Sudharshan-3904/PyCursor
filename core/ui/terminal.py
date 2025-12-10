import os
import platform
from PyQt6.QtCore import QProcess, QProcessEnvironment, Qt
from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from PyQt6.QtGui import QTextCursor
from core.ui.theme import COLORS


class Terminal(QTextEdit):
    def __init__(self, project_path=None):
        super().__init__()
        self.setReadOnly(False)
        self.setAcceptRichText(False)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
                border: none;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(100)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setUndoRedoEnabled(False)

        self.project_path = project_path or os.getcwd()
        self.shell = self._detect_shell()
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_output)
        self.process.readyReadStandardError.connect(self._on_output)

        if os.path.isdir(self.project_path):
            self.process.setWorkingDirectory(self.project_path)

        env = QProcessEnvironment.systemEnvironment()

        for key, value in os.environ.items():
            env.insert(str(key), str(value))

        activate_cmd = self._get_env_activation_path()
        if activate_cmd and os.path.exists(activate_cmd):
            venv_dir = os.path.join(activate_cmd, "..")
            path = env.value("PATH") or ""
            env.insert("PATH", venv_dir + os.pathsep + path)

        self.process.setProcessEnvironment(env)

        shell_prog = self.shell
        shell_args = []
        if platform.system() == "Windows":
            lower = shell_prog.lower()
            if "powershell" in lower or "pwsh" in lower:
                shell_args = ["-NoExit"]
            else:
                shell_args = ["/K"]
        else:
            base = os.path.basename(shell_prog)
            if base in ("bash", "zsh", "sh"):
                shell_args = ["-i"]

        if shell_args:
            self.process.start(shell_prog, shell_args)
        else:
            self.process.start(shell_prog)

        if not self.process.waitForStarted(3000):
            self.append("[Terminal] Failed to start shell process")

        self.prompt = f"{self.project_path} $ " if os.name != "nt" else f"{self.project_path}> "
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        self.append(self.prompt)

    def _detect_shell(self):
        if platform.system() == "Windows":
            return os.environ.get("COMSPEC", "cmd.exe")
        elif platform.system() == "Darwin":
            return os.environ.get("SHELL", "/bin/zsh")
        else:
            return os.environ.get("SHELL", "/bin/bash")

    def _get_env_activation_path(self):
        venv_path = os.path.join(self.project_path, "venv")
        if os.path.exists(venv_path):
            if platform.system() == "Windows":
                return os.path.join(venv_path, "Scripts", "python.exe")
            else:
                return os.path.join(venv_path, "bin", "python")
        return None

    def _on_output(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        if data:
            self.moveCursor(QTextCursor.MoveOperation.End)
            self.insertPlainText(data)
            self.ensureCursorVisible()

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            last_line = self.toPlainText().split("\n")[-1]
            cmd = last_line
            if self.prompt and self.prompt in last_line:
                cmd = last_line.replace(self.prompt, "", 1)
            else:
                for sep in (">", "$", ":"):
                    idx = last_line.rfind(sep)
                    if idx != -1:
                        cmd = last_line[idx + 1 :].lstrip()
                        break

            cmd = cmd.strip()
            if cmd and cmd.lower() in ("cls", "clear"):
                self.clear()
                self.append(self.prompt)
                return

            if cmd:
                newline = "\r\n" if platform.system() == "Windows" else "\n"
                self.process.write((cmd + newline).encode("utf-8"))
            self.append("")
            return

        elif event.key() == Qt.Key.Key_Backspace:
            line = self.toPlainText().split("\n")[-1]
            if len(line) <= len(self.prompt):
                return

        super().keyPressEvent(event)
    
    def log(self, msgStr: str = ""):
        self.append("-"*75)
        self.append(f"[Log] ::: {msgStr}")
        self.append("-"*75)

    def execute_command(self, command: str):
        if not self.process.state() == QProcess.ProcessState.Running:
            return
        
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        
        self.append("\n" + "="*75)
        self.append(f">>> Executing: {command}")
        self.append("="*75 + "\n")
        
        self.process.write((command + "\n").encode("utf-8"))
        self.ensureCursorVisible()

    def set_project_path(self, new_path: str):
        """Update the project path and change directory in the terminal."""
        if not os.path.isdir(new_path):
            return
        
        self.project_path = new_path
        self.prompt = f"{self.project_path} $ " if os.name != "nt" else f"{self.project_path}> "
        
        if self.process.state() == QProcess.ProcessState.Running:
            cd_command = f"cd \"{new_path}\"" if os.name == "nt" else f"cd '{new_path}'"
            self.execute_command(cd_command)
