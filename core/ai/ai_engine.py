import sys
import re
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMenu,
    QTextEdit, QPushButton, QLineEdit, QInputDialog, QMessageBox,
    QLabel
)
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QFontInfo
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

        # Asset Initialization & Caching
        self._icon_cache = {}
        self.send_icon = self._get_cached_icon("send.png")
        self.local_icon = self._get_cached_icon("local.png")
        self.api_icon = self._get_cached_icon("api.png")
        self.model_icon = self._get_cached_icon("model.png")
        self.agent_icon = self._get_cached_icon("agent.svg")
        self.brain_icon = self._get_cached_icon("brain.svg")

        # Pre-compiled Regex Patterns
        self._re_read = re.compile(r'<read_file>(.*?)</read_file>', re.DOTALL)
        self._re_write = re.compile(r'<write_file path="(.*?)">(.*?)</write_file>', re.DOTALL)
        self._re_edit = re.compile(r'<<<edit>>>(.*?)<<</edit>>>', re.DOTALL)

        # Backend Handlers
        self.local_model_handler = LocalModelHandler()
        self.api_model_handler = APIModelHandler()
        self.docstring_generator = DocstringGenerator(style='google')
        self.code_linter = CodeLinter()
        self.context_manager = ContextManager()

        # State Management
        self.models = {
            "LM Studio": ["lm1", "lm2"],
            "Ollama": ["granite", "ruby"],
            "API": ["ChatGPT Go"]
        }
        self.current_model_name = "lm1"
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
        
        # Set font to prevent invalid font sizes
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            font = QFont("Courier New", 10)
            font.setPointSize(10)
        self.chat_area.setFont(font)
        
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
        self.api_local_btn.setObjectName("AIChatControl")
        self.api_local_btn.setIcon(self.local_icon)
        self.api_local_btn.setCheckable(True)
        self.api_local_btn.setFixedHeight(28)
        self.api_local_btn.setToolTip("Toggle API/Local")
        self.api_local_btn.clicked.connect(self.toggle_api_local)
        toolbar.addWidget(self.api_local_btn)
        
        # Agent Mode Toggle (Grants FS access permissions)
        self.agent_mode_btn = QPushButton()
        self.agent_mode_btn.setObjectName("AIChatControl")
        self.agent_mode_btn.setIcon(self.agent_icon)
        self.agent_mode_btn.setCheckable(True)
        self.agent_mode_btn.setFixedHeight(28)
        self.agent_mode_btn.setToolTip("Agentic Mode")
        self.agent_mode_btn.clicked.connect(self.toggle_agent_mode)
        toolbar.addWidget(self.agent_mode_btn)

        # Brain Mode Toggle (Enables RAG)
        self.brain_mode_btn = QPushButton()
        self.brain_mode_btn.setObjectName("AIChatControl")
        self.brain_mode_btn.setIcon(self.brain_icon)
        self.brain_mode_btn.setCheckable(True)
        self.brain_mode_btn.setFixedHeight(28)
        self.brain_mode_btn.setToolTip("Brain Mode (Project Index)")
        self.brain_mode_btn.clicked.connect(self.toggle_brain_mode)
        toolbar.addWidget(self.brain_mode_btn)

        # Model Selector Menu
        self.model_btn = QPushButton()
        self.model_btn.setObjectName("AIChatControl")
        self.model_btn.setIcon(self.model_icon)
        self.model_btn.setFixedHeight(28)
        self.model_btn.setToolTip("Select Model")
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

        # Reference list area
        self.reference_label = QLabel("References: None")
        self.reference_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        layout.addWidget(self.reference_label)

    def refresh_icons(self, theme_name):
        """
        Updates AI engine icons to match the current theme palette.
        """
        from core.ui.theme import get_icon_color
        color = get_icon_color(theme_name)
        
        self.send_btn.setIcon(self._get_cached_icon("send.png", color=color))
        self.model_btn.setIcon(self._get_cached_icon("model.png", color=color))
        self.agent_mode_btn.setIcon(self._get_cached_icon("agent.svg", color=color))
        self.brain_mode_btn.setIcon(self._get_cached_icon("brain.svg", color=color))
        
        # Source Toggle Icon
        source_icon = "local.png" if not self.using_api else "api.png"
        self.api_local_btn.setIcon(self._get_cached_icon(source_icon, color=color))

    def _get_cached_icon(self, name, color=None):
        """
        Retrieves an icon from the internal cache or loads it if missing.
        """
        cache_key = (name, color.name() if color else None)
        if cache_key not in self._icon_cache:
            self._icon_cache[cache_key] = load_icon(name, color=color)
        return self._icon_cache[cache_key]

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
        Updates the active model backend and target identifier with robust parsing.
        """
        backend = "api"
        identifier = selected_model
        
        if ": " in selected_model:
            parts = selected_model.split(": ", 1)
            prefix = parts[0].lower()
            if "ollama" in prefix:
                backend = "ollama"
            elif "lm studio" in prefix:
                backend = "lmstudio"
            identifier = parts[1]

        self.local_model_handler.backend = backend
        self.local_model_handler.model_name = identifier
        self.current_model_name = identifier
        self.current_backend = backend

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

    def toggle_brain_mode(self):
        """
        Enables RAG (Project-Wide Context) mode.
        """
        self.context_manager.rag_enabled = self.brain_mode_btn.isChecked()
        if self.context_manager.rag_enabled:
            self.chat_area.append("<i>[Brain Mode Enabled - Projects indexed for context]</i>")

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
        used_files = context_data.get("files", [])
        
        if used_files:
            self.reference_label.setText(f"References: {', '.join(used_files[:3])}{'...' if len(used_files) > 3 else ''}")
        else:
            self.reference_label.setText("References: None")
        
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
        Supports atomic multi-file transactions with rollback capabilities.
        """
        modified = response
        self.last_transaction = [] # List of (path, original_content)
        
        # Handle read_file
        for match in self._re_read.finditer(response):
            path = match.group(1).strip()
            try:
                full_path = os.path.join(getattr(self.main_window, 'project_path', '.'), path)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                modified = modified.replace(match.group(0), f"\n```\n{content}\n```\n")
            except Exception as e:
                modified = modified.replace(match.group(0), f"[Read Error: {e}]")

        # Handle write_file (Transaction-aware)
        for match in self._re_write.finditer(response):
            path, content = match.group(1).strip(), match.group(2).strip()
            try:
                full_path = os.path.join(getattr(self.main_window, 'project_path', '.'), path)
                
                # Backup for rollback
                orig = ""
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f: orig = f.read()
                self.last_transaction.append((full_path, orig))

                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
                modified = modified.replace(match.group(0), f"[Success: Wrote to {path}]")
            except Exception as e:
                modified = modified.replace(match.group(0), f"[Write Error: {e}]")

        if self.last_transaction:
            self.chat_area.append(f"<i>[Multi-file update applied. {len(self.last_transaction)} files modified. <a href='rollback'>Undo</a>]</i>")
            
        return modified

    def rollback_last_transaction(self):
        """
        Restores files to their pre-transaction state.
        """
        if not hasattr(self, 'last_transaction') or not self.last_transaction:
            return
            
        for path, content in self.last_transaction:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                self.chat_area.append(f"<i>[Rollback Error for {path}: {e}]</i>")
        
        self.chat_area.append("<i>[Rollback completed successfully]</i>")
        self.last_transaction = []

    def apply_response_to_editor(self, response: str):
        """
        Extracts code from edit tags and injects it into the active editor buffer.
        """
        match = self._re_edit.search(response)
        extracted = match.group(1).strip() if match else response.strip()

        editor = getattr(self.main_window, 'editor_manager', None).get_current_editor() if hasattr(self, 'main_window') else None
        if editor:
            # Use append_text if the response is just supplementary, or setText if it is meant to replace
            # For <<<edit>>> tags, we'll append to the end for now.
            if hasattr(editor, 'append_text'):
                editor.append_text(extracted)
            else:
                current = editor.text()
                new_code = (current + "\n" + extracted) if current and not current.endswith("\n") else (current + extracted)
                editor.setText(new_code)
            
            # Auto-save changes
            if hasattr(self.main_window, 'editor_manager'):
                self.main_window.editor_manager.save_current_file()

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
