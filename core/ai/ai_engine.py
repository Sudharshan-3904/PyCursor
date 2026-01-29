import sys
import re
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMenu,
    QTextEdit, QPushButton, QLineEdit, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ..utilities.utils import load_icon
from .local_model_handler import LocalModelHandler
from .api_model_handler import APIModelHandler, APIConfig
from .docstring_generator import DocstringGenerator
from .code_linter import CodeLinter
from core.ui.theme import COLORS
from core.utilities.worker import WorkerThread
from core.ai.context_manager import ContextManager

class AIEngine(QWidget):
    """
    Central AI Intelligence Hub for PyCursor IDE.
    Provides a chat interface, model management (local/API), and specialized 
    coding agents (Agentic mode, Refactoring, Linting).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.resize(600, 800)

        # Asset Initialization
        self.send_icon = load_icon("send.png")
        self.local_icon = load_icon("local.png")
        self.api_icon = load_icon("api.png")
        self.model_icon = load_icon("model.png")

        # Backend Handlers
        self.local_model_handler = LocalModelHandler()
        self.api_model_handler = APIModelHandler()
        self.docstring_generator = DocstringGenerator(style='google')
        self.code_linter = CodeLinter()
        self.context_manager = ContextManager()

        # State Management
        self.models = {}
        self.current_model_name = None
        self.current_backend = "ollama"
        self.api_config = None
        self.using_api = False
        self.agent_mode = False

        self._init_ui()

    def _init_ui(self):
        """
        Constructs the AI assistant UI including the chat history, 
        input field, and management toolbar.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Chat display area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.chat_area)

        # Prompt input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AI about your code...")
        self.input_field.returnPressed.connect(self.handle_send)
        layout.addWidget(self.input_field)

        # Toolbar for Model/Agent controls
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)

        # Source Toggle (Local vs Cloud API)
        self.api_local_btn = QPushButton()
        self.api_local_btn.setIcon(self.local_icon)
        self.api_local_btn.setCheckable(True)
        self.api_local_btn.setFixedHeight(28)
        self.api_local_btn.clicked.connect(self.toggle_api_local)
        toolbar.addWidget(self.api_local_btn)
        
        # Agent Mode Toggle (Grants FS access permissions)
        self.agent_mode_btn = QPushButton("Agent")
        self.agent_mode_btn.setCheckable(True)
        self.agent_mode_btn.setFixedHeight(28)
        self.agent_mode_btn.clicked.connect(self.toggle_agent_mode)
        toolbar.addWidget(self.agent_mode_btn)

        # Model Selector Menu
        self.model_btn = QPushButton()
        self.model_btn.setIcon(self.model_icon)
        self.model_btn.setFixedHeight(28)
        self.model_menu = QMenu(self)
        self.model_btn.setMenu(self.model_menu)
        toolbar.addWidget(self.model_btn)

        toolbar.addStretch()

        # Send Button
        self.send_btn = QPushButton()
        self.send_btn.setIcon(self.send_icon)
        self.send_btn.setFixedHeight(28)
        self.send_btn.clicked.connect(self.handle_send)
        toolbar.addWidget(self.send_btn)

        layout.addLayout(toolbar)

    def update_models(self, models: dict):
        """
        Refreshes the available model registry discovered by the startup thread.
        """
        self.models = models
        if not self.current_model_name and self.models:
            self.current_model_name = next(iter(self.models.keys()), None)
            self.on_model_change(self.current_model_name)
        self._populate_model_menu()

    def _populate_model_menu(self):
        """
        Categorizes and displays discovered models in the selection menu.
        """
        self.model_menu.clear()

        for group, prefix in [("LM Studio", "LM Studio"), ("Ollama", "Ollama"), ("API", "api")]:
            group_models = [n for n in self.models if n.startswith(prefix)]
            if group_models:
                header = QAction(f"{group} Models", self)
                header.setEnabled(False)
                self.model_menu.addAction(header)
                for m in group_models:
                    act = QAction(m.split(": ", 1)[-1], self)
                    act.triggered.connect(lambda checked=False, model=m: self.on_model_change(model))
                    self.model_menu.addAction(act)
                self.model_menu.addSeparator()

    def on_model_change(self, selected_model):
        """
        Updates the active model backend and target identifier.
        """
        if selected_model.startswith("Ollama:"):
            backend, identifier = "ollama", selected_model.split(": ", 1)[-1]
        elif selected_model.startswith("LM Studio:"):
            backend, identifier = "lmstudio", selected_model.split(": ", 1)[-1]
        else:
            backend, identifier = "api", selected_model

        self.local_model_handler.backend = backend
        self.local_model_handler.model_name = identifier

    def toggle_api_local(self):
        """
        Switches between local execution and cloud API execution.
        """
        self.using_api = self.api_local_btn.isChecked()
        self.api_local_btn.setIcon(self.api_icon if self.using_api else self.local_icon)
    
    def toggle_agent_mode(self):
        """
        Enables agentic capabilities, allowing the AI to request file system operations.
        """
        self.agent_mode = self.agent_mode_btn.isChecked()

    def handle_send(self):
        """
        Processes user query, gathers project context, and dispatches prediction request.
        """
        user_input = self.input_field.text().strip()
        if not user_input: return

        self.chat_area.append(f"<b>User:</b> {user_input}")
        self.input_field.clear()
        
        # Determine project context
        project_path = getattr(self.main_window, 'project_path', None) if hasattr(self, 'main_window') else None
        self.context_manager.set_project_path(project_path)
        
        context_data = self.context_manager.get_context(user_input)
        context_text = context_data.get("text", "")
        
        # Build systematic prompt
        prompt_parts = []
        if self.agent_mode:
            prompt_parts.append("You are an AI agent. Use <read_file>, <write_file>, <create_file>, <list_dir> for FS tasks.")
        
        if context_text: prompt_parts.append(context_text)
        prompt_parts.append(f"Request: {user_input}")
        
        full_prompt = "\n\n".join(prompt_parts)

        # Dispatch task to background worker
        if self.using_api:
            self.worker = WorkerThread(lambda p, m: self.api_model_handler.generate_response(p), full_prompt, "default")
        else:
            self.worker = WorkerThread(self.local_model_handler.local_model_response, full_prompt)
        
        self.worker.result_ready.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self._handle_ai_error)
        self.worker.finished.connect(self._on_worker_finished)
        
        self.send_btn.setEnabled(False)
        self.chat_area.append("<i>Processing...</i>")
        self.worker.start()

    def handle_ai_response(self, response):
        """
        Processes prediction output, executing agent commands or applying code edits.
        """
        if self.agent_mode:
            response = self.process_agent_commands(response)

        if "<<<edit>>>" in response:
            try:
                self.apply_response_to_editor(response)
                self.chat_area.append("<i>[Applied code changes to editor]</i>")
            except Exception as e:
                self.chat_area.append(f"<i>[Editor Update Error: {e}]</i>")
        else:
            self.chat_area.append(f"<b>AI:</b> {response}\n")
            
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def process_agent_commands(self, response: str) -> str:
        """
        Parses and executes file system XML tags returned by the AI agent.
        """
        modified = response
        
        # Handle read_file
        read_pattern = r'<read_file>(.*?)</read_file>'
        for match in re.finditer(read_pattern, response):
            path = match.group(1).strip()
            try:
                with open(os.path.join(getattr(self.main_window, 'project_path', '.'), path), 'r', encoding='utf-8') as f:
                    content = f.read()
                modified = modified.replace(match.group(0), f"\n```\n{content}\n```\n")
            except Exception as e:
                modified = modified.replace(match.group(0), f"[Read Error: {e}]")

        # Handle write_file
        write_pattern = r'<write_file path="(.*?)">(.*?)</write_file>'
        for match in re.finditer(write_pattern, response, re.DOTALL):
            path, content = match.group(1).strip(), match.group(2).strip()
            try:
                full_path = os.path.join(getattr(self.main_window, 'project_path', '.'), path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
                modified = modified.replace(match.group(0), f"[Success: Wrote to {path}]")
            except Exception as e:
                modified = modified.replace(match.group(0), f"[Write Error: {e}]")

        return modified

    def apply_response_to_editor(self, response: str):
        """
        Extracts code from edit tags and injects it into the active editor buffer.
        """
        match = re.search(r'<<<edit>>>(.*?)<<</edit>>>', response, re.DOTALL)
        extracted = match.group(1).strip() if match else response.strip()

        editor = getattr(self.main_window, 'editor_manager', None).get_current_editor() if hasattr(self, 'main_window') else None
        if editor:
            current = editor.text()
            new_code = (current + "\n" + extracted) if current and not current.endswith("\n") else (current + extracted)
            editor.setText(new_code)
            
            # Auto-save changes
            path = getattr(editor, 'file_path', None)
            if path:
                with open(path, "w", encoding="utf-8") as f: f.write(new_code)

    def _handle_ai_error(self, error):
        self.chat_area.append(f"<span style='color:red'>AI Error: {error}</span>")

    def _on_worker_finished(self):
        self.send_btn.setEnabled(True)
        self.input_field.setFocus()

    def set_main_window(self, main_window):
        self.main_window = main_window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AIEngine()
    widget.show()
    sys.exit(app.exec())
