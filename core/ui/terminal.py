import sys
import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QLineEdit, 
    QComboBox,
    QLabel,
    QTabWidget,
    QApplication,
)
from PyQt6.QtCore import QProcess, Qt

class TerminalTab(QWidget):
    def __init__(self, shell=None, env=None, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.env = env
        self.shell = shell or (os.environ.get('SHELL') if os.name != 'nt' else 'cmd.exe')
        self.initUI()
        self.setupProcess()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Output
        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setStyleSheet("font-family: monospace;")
        layout.addWidget(self.output)

        # Input
        input_layout = QHBoxLayout()
        self.input = QLineEdit(self)
        self.input.returnPressed.connect(self.sendCommand)
        input_layout.addWidget(QLabel(">"))
        input_layout.addWidget(self.input)
        layout.addLayout(input_layout)

    def setupProcess(self):
        if self.env:
            env = self.process.processEnvironment()
            for key, value in self.env.items():
                env.insert(key, value)
            self.process.setProcessEnvironment(env)

        # Start the shell process
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyRead.connect(self.processOutput)
        self.process.start(self.shell)

    def sendCommand(self):
        cmd = self.input.text()
        if cmd.strip() == "":
            return
        self.output.appendPlainText(f"> {cmd}")
        if not cmd.endswith('\n'):
            cmd += '\n'
        # Write to the process
        self.process.write(cmd.encode("utf-8"))
        self.input.clear()

    def processOutput(self):
        data = self.process.readAll().data().decode("utf-8", errors="replace")
        self.output.appendPlainText(data)

    def closeEvent(self, event):
        self.process.kill()
        super().closeEvent(event)

class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Button row for tab controls
        tab_btn_layout = QHBoxLayout()
        new_tab_btn = QPushButton("New Terminal")
        new_tab_btn.clicked.connect(self.addTab)
        tab_btn_layout.addWidget(new_tab_btn)
        tab_btn_layout.addStretch()
        layout.addLayout(tab_btn_layout)
    
        
        shell_selector = QComboBox()
        shell_selector.addItems(SHELLS.keys())
        shell_selector.currentTextChanged.connect(self.change_shell)

        # First tab by default
        self.addTab()

    def addTab(self):
        tab_count = self.tabs.count() + 1
        term_tab = TerminalTab()
        self.tabs.addTab(term_tab, f'Terminal {tab_count}')
        self.tabs.setCurrentWidget(term_tab)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TerminalWidget()
    win.setWindowTitle("PyCursor Terminal")
    win.resize(800, 400)
    win.show()
    sys.exit(app.exec())
