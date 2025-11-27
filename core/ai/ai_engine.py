import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMenu,
    QTextEdit, QPushButton, QLineEdit, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QAction

from ..utilities.utils import load_icon
from .local_model_handler import LocalModelHandler
from .api_model_handler import APIModelHandler, APIConfig
from .docstring_generator import DocstringGenerator
from .code_linter import CodeLinter


from core.ui.theme import COLORS

class AIEngine(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.resize(600, 800)

        self.chunk_size = 500

        self.send_icon = load_icon("send.png")
        self.local_icon = load_icon("local.png")
        self.api_icon = load_icon("api.png")
        self.model_icon = load_icon("model.png")

        self.local_model_handler = LocalModelHandler()

        self.models = self.local_model_handler.detect_models()
        self.current_model_name = next(iter(self.models.keys()), None)
        self.current_backend = (
            "lmstudio" if self.current_model_name and self.current_model_name.startswith("LM Studio") else "ollama"
        )

        self.local_model_handler.backend = self.current_backend
        self.local_model_handler.model_name = (
            self.current_model_name.split(": ", 1)[-1] if self.current_model_name else None
        )

        self.api_model_handler = APIModelHandler()
        self.api_config = None
        
        self.docstring_generator = DocstringGenerator(style='google')
        
        self.code_linter = CodeLinter()

        self.using_api = False

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.chat_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['editor_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        main_layout.addWidget(self.chat_area)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.handle_send)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['border_focus']};
                background-color: {COLORS['bg_primary']};
            }}
        """)
        main_layout.addWidget(self.input_field)



        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)

        self.api_local_btn = QPushButton()
        self.api_local_btn.setIcon(self.local_icon)
        self.api_local_btn.setCheckable(True)
        self.api_local_btn.setFixedHeight(28)
        self.api_local_btn.clicked.connect(self.toggle_api_local)
        self.api_local_btn.setToolTip("Toggle between Local and API models")
        toolbar_layout.addWidget(self.api_local_btn)
        
        # Agent mode toggle
        self.agent_mode = False
        self.agent_mode_btn = QPushButton("Agent")
        self.agent_mode_btn.setCheckable(True)
        self.agent_mode_btn.setFixedHeight(28)
        self.agent_mode_btn.setChecked(False)
        self.agent_mode_btn.clicked.connect(self.toggle_agent_mode)
        self.agent_mode_btn.setToolTip("Enable Agent Mode (AI can read/write files)")
        self.agent_mode_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QPushButton:checked {{
                background-color: {COLORS['accent_green']};
                color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['accent_green']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_elevated']};
            }}
        """)
        toolbar_layout.addWidget(self.agent_mode_btn)

        self.model_btn = QPushButton()
        self.model_btn.setIcon(self.model_icon)
        self.model_btn.setFixedHeight(28)
        self.model_btn.setToolTip("Select AI Model")

        self.model_menu = QMenu(self)
        self.populate_model_menu()
        self.model_btn.setMenu(self.model_menu)
        toolbar_layout.addWidget(self.model_btn)

        toolbar_layout.addStretch()

        self.send_btn = QPushButton()
        self.send_btn.setIcon(self.send_icon)
        self.send_btn.setFixedHeight(28)
        self.send_btn.setToolTip("Send message")
        self.send_btn.clicked.connect(self.handle_send)
        toolbar_layout.addWidget(self.send_btn)

        main_layout.addLayout(toolbar_layout)

        self.setLayout(main_layout)


    def populate_model_menu(self):
        self.model_menu.clear()

        lm_studio_models = [name for name in self.models if name.startswith("LM Studio")]
        if lm_studio_models:
            lm_studio_header = QAction("LM Studio models", self)
            lm_studio_header.setEnabled(False)
            self.model_menu.addAction(lm_studio_header)

            for model in lm_studio_models:
                action = QAction(model.split(": ", 1)[-1], self)
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)
            self.model_menu.addSeparator()

        ollama_models = [name for name in self.models if name.startswith("Ollama")]
        if ollama_models:
            ollama_header = QAction("Ollama models", self)
            ollama_header.setEnabled(False)
            self.model_menu.addAction(ollama_header)

            for model in ollama_models:
                action = QAction(model.split(": ", 1)[-1], self)
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)
            self.model_menu.addSeparator()

        api_models = ["chat gpt go"]
        if api_models:
            api_header = QAction("API models", self)
            api_header.setEnabled(False)
            self.model_menu.addAction(api_header)

            for model in api_models:
                action = QAction(model, self)
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)

    def on_model_change(self, selected_model):
        if selected_model.startswith("Ollama:"):
            backend = "ollama"
            model_identifier = selected_model.split(": ", 1)[-1]
        elif selected_model.startswith("LM Studio:"):
            backend = "lmstudio"
            model_identifier = selected_model.split(": ", 1)[-1]
        else:
            backend = "api"
            model_identifier = selected_model

        self.local_model_handler.backend = backend
        self.local_model_handler.model_name = model_identifier

        self.chat_area.append(f"<i>[Switched to {backend} model: {model_identifier}]</i>")

    def choose_model(self):
        model_names = list(self.models.keys())
        if not model_names:
            return

        item, ok = QInputDialog.getItem(
            self,
            "Select Model",
            "Choose a model to use:",
            model_names,
            current=0,
            editable=False
        )
        if ok and item:
            self.current_model_name = item
            self.current_backend = "lmstudio" if item.startswith("LM Studio") else "ollama"

            self.local_model_handler = LocalModelHandler(
                backend=self.current_backend,
                model_name=item.split(": ", 1)[-1]
            )
            self.chat_area.append(f"<i>[Model switched to: {self.current_model_name}]</i>")

    def toggle_api_local(self):
        self.using_api = self.api_local_btn.isChecked()
        if self.using_api:
            self.api_local_btn.setIcon(self.api_icon)
            self.api_local_btn.setToolTip("Using API models")
        else:
            self.api_local_btn.setIcon(self.local_icon)
            self.api_local_btn.setToolTip("Using Local models")
    
    def toggle_agent_mode(self):
        """Toggle agent mode on/off"""
        self.agent_mode = self.agent_mode_btn.isChecked()
        if self.agent_mode:
            self.chat_area.append("<i>[Agent Mode ENABLED - AI can now read, create, and write files]</i>")
        else:
            self.chat_area.append("<i>[Agent Mode DISABLED - AI responses only]</i>")


    def api_model_response(self, prompt, model_identifier):
        """Generate response using API models"""
        if not self.api_config:
            return "[Error: API not configured. Please configure API settings first.]"
        
        try:
            response = self.api_model_handler.generate_response(prompt)
            return response
        except Exception as e:
            return f"[API Error: {e}]"
    
    def set_main_window(self, main_window):
        self.main_window = main_window

    def run_model(self, prompt: str) -> str:
        try:
            resp = self.local_model_handler.local_model_response(prompt)

            if isinstance(resp, str):
                return resp

            if hasattr(resp, "__iter__") and not isinstance(resp, (dict, bytes)):
                buffer = []
                for chunk in resp:
                    if hasattr(chunk, "text"):
                        buffer.append(chunk.text)
                    else:
                        buffer.append(str(chunk))
                return "".join(buffer)

            return str(resp)

        except Exception as e:
            return f"[AI Error] {e}"

    def _contains_edit_tags(self, response: str) -> bool:
        return "<<<edit>>>" in response and "<<</edit>>>" in response

    def handle_send(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"<b>User:</b> {user_input}")
        self.input_field.clear()
        
        # Prepare prompt with agent mode context if enabled
        if self.agent_mode:
            system_context = """You are an AI agent with file system access. You can:
- Read files: Use <read_file>path/to/file.py</read_file>
- Write files: Use <write_file path="path/to/file.py">content here</write_file>
- Create files: Use <create_file path="path/to/file.py">content here</create_file>
- List directory: Use <list_dir>path/to/directory</list_dir>

When the user asks you to work with files, use these tags in your response.
For code edits, use <<<edit>>> tags as usual."""
            
            full_prompt = f"{system_context}\n\nUser request: {user_input}"
        else:
            full_prompt = user_input

        if self.using_api:
            model_identifier = next(iter(self.models.values()), "default")
            response = self.api_model_response(full_prompt, model_identifier)
        else:
            response = self.run_model(full_prompt)
        
        # Handle agent mode file operations
        if self.agent_mode:
            response = self.process_agent_commands(response)

        if self._contains_edit_tags(response):
            try:
                self.apply_response_to_editor(response)
                self.chat_area.append("<i>[AI wrote changes to the editor]</i>")
            except Exception as e:
                self.chat_area.append(f"<i>[Failed to apply response to editor: {e}]</i>")
            return

        self.chat_area.append(f"<b>AI:</b> {response}\n")
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def process_agent_commands(self, response: str) -> str:
        """Process agent mode file operation commands"""
        import os
        import re
        
        modified_response = response
        
        # Handle read_file
        read_pattern = r'<read_file>(.*?)</read_file>'
        for match in re.finditer(read_pattern, response):
            file_path = match.group(1).strip()
            try:
                # Get project path
                project_path = getattr(self.main_window, 'project_path', os.getcwd()) if hasattr(self, 'main_window') else os.getcwd()
                full_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.chat_area.append(f"<i>[Read file: {file_path}]</i>")
                modified_response = modified_response.replace(match.group(0), f"\n```\n{content}\n```\n")
            except Exception as e:
                self.chat_area.append(f"<i>[Error reading {file_path}: {e}]</i>")
                modified_response = modified_response.replace(match.group(0), f"[Error: {e}]")
        
        # Handle write_file
        write_pattern = r'<write_file path="(.*?)">(.*?)</write_file>'
        for match in re.finditer(write_pattern, response, re.DOTALL):
            file_path = match.group(1).strip()
            content = match.group(2).strip()
            try:
                project_path = getattr(self.main_window, 'project_path', os.getcwd()) if hasattr(self, 'main_window') else os.getcwd()
                full_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.chat_area.append(f"<i>[✓ Wrote to file: {file_path}]</i>")
                modified_response = modified_response.replace(match.group(0), f"[File written: {file_path}]")
            except Exception as e:
                self.chat_area.append(f"<i>[Error writing {file_path}: {e}]</i>")
                modified_response = modified_response.replace(match.group(0), f"[Error: {e}]")
        
        # Handle create_file
        create_pattern = r'<create_file path="(.*?)">(.*?)</create_file>'
        for match in re.finditer(create_pattern, response, re.DOTALL):
            file_path = match.group(1).strip()
            content = match.group(2).strip()
            try:
                project_path = getattr(self.main_window, 'project_path', os.getcwd()) if hasattr(self, 'main_window') else os.getcwd()
                full_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.chat_area.append(f"<i>[✓ Created file: {file_path}]</i>")
                modified_response = modified_response.replace(match.group(0), f"[File created: {file_path}]")
            except Exception as e:
                self.chat_area.append(f"<i>[Error creating {file_path}: {e}]</i>")
                modified_response = modified_response.replace(match.group(0), f"[Error: {e}]")
        
        # Handle list_dir
        list_pattern = r'<list_dir>(.*?)</list_dir>'
        for match in re.finditer(list_pattern, response):
            dir_path = match.group(1).strip()
            try:
                project_path = getattr(self.main_window, 'project_path', os.getcwd()) if hasattr(self, 'main_window') else os.getcwd()
                full_path = os.path.join(project_path, dir_path) if not os.path.isabs(dir_path) else dir_path
                
                items = os.listdir(full_path)
                items_str = "\n".join(f"  - {item}" for item in sorted(items))
                
                self.chat_area.append(f"<i>[Listed directory: {dir_path}]</i>")
                modified_response = modified_response.replace(match.group(0), f"\nDirectory contents:\n{items_str}\n")
            except Exception as e:
                self.chat_area.append(f"<i>[Error listing {dir_path}: {e}]</i>")
                modified_response = modified_response.replace(match.group(0), f"[Error: {e}]")
        
        return modified_response


    def apply_response_to_editor(self, response: str):
        if "<<<edit>>>" in response and "<<</edit>>>" in response:
            start = response.find("<<<edit>>>") + len("<<<edit>>>")
            end = response.find("<<</edit>>>")

            extracted = response[start:end].strip()
        else:
            extracted = response.strip()

        if not extracted:
            self.chat_area.append("<i>[No content extracted]</i>")
            return

        if not hasattr(self, "main_window"):
            self.chat_area.append("<i>[No main window attached]</i>")
            return

        try:
            editor = self.main_window.get_current_editor()
        except Exception:
            editor = None

        if editor is None:
            self.chat_area.append("<i>[No active editor, writing to fallback file]</i>")
            return

        if hasattr(editor, "toPlainText"):
            current = editor.toPlainText()
        elif hasattr(editor, "text"):
            current = editor.text()
        elif hasattr(editor, "get_text"):
            current = editor.get_text()
        else:
            raise AttributeError("Editor has no method to get text")

        if current is None:
            current = ""

        if current and not current.endswith("\n"):
            new_content = current + "\n" + extracted
        else:
            new_content = current + extracted

        if hasattr(editor, "setPlainText"):
            editor.setPlainText(new_content)
        elif hasattr(editor, "set_text"):
            editor.set_text(new_content)
        elif hasattr(editor, "setText"):
            editor.setText(new_content)
        else:
            raise AttributeError("Editor has no method to set text")

        file_path = getattr(editor, "file_path", None)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

        added_lines = len(extracted.splitlines())
        self.chat_area.append(f"<i>[AI added {added_lines} lines]</i>")
    
    def configure_api(self, provider: str):
        """
        Configure API settings for a provider
        
        Args:
            provider: 'openai', 'anthropic', or 'gemini'
        """
        from PyQt6.QtWidgets import QDialog, QFormLayout, QComboBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Configure {provider.title()} API")
        dialog.resize(400, 200)
        
        layout = QFormLayout()
        
        api_key_input = QLineEdit()
        api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_input.setPlaceholderText("Enter API key or leave empty to use environment variable")
        layout.addRow("API Key:", api_key_input)
        
        model_combo = QComboBox()
        models = APIModelHandler.get_available_models(provider)
        model_combo.addItems(models)
        layout.addRow("Model:", model_combo)
        
        temp_input = QLineEdit("0.7")
        layout.addRow("Temperature:", temp_input)
        
        tokens_input = QLineEdit("2000")
        layout.addRow("Max Tokens:", tokens_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_key = api_key_input.text().strip()
            if not api_key:
                api_key = APIModelHandler.load_api_key_from_env(provider)
            
            if not api_key:
                QMessageBox.warning(self, "API Key Required", 
                                  f"No API key provided and none found in environment variable")
                return
            
            try:
                self.api_config = APIConfig(
                    provider=provider,
                    api_key=api_key,
                    model_name=model_combo.currentText(),
                    temperature=float(temp_input.text()),
                    max_tokens=int(tokens_input.text())
                )
                self.api_model_handler.set_config(self.api_config)
                self.chat_area.append(f"<i>[API configured: {provider} - {model_combo.currentText()}]</i>")
            except Exception as e:
                QMessageBox.critical(self, "Configuration Error", f"Failed to configure API: {e}")
    
    def generate_docstring_for_current_code(self):
        """Generate docstring for code in current editor"""
        if not hasattr(self, 'main_window'):
            self.chat_area.append("<i>[No main window attached]</i>")
            return
        
        try:
            editor = self.main_window.get_current_editor()
            if editor is None:
                self.chat_area.append("<i>[No active editor]</i>")
                return
            
            if hasattr(editor, 'toPlainText'):
                code = editor.toPlainText()
            elif hasattr(editor, 'text'):
                code = editor.text()
            else:
                self.chat_area.append("<i>[Cannot read editor content]</i>")
                return
            
            missing = self.docstring_generator.find_missing_docstrings(code)
            
            if not missing:
                self.chat_area.append("<i>[All functions and classes have docstrings!]</i>")
                return
            
            self.chat_area.append(f"<b>Found {len(missing)} items missing docstrings:</b>")
            for item in missing:
                self.chat_area.append(f"  - {item['type']}: {item['name']} (line {item['line']})")
            
            analysis = self.docstring_generator.analyze_code(code)
            
            if analysis['functions']:
                func = analysis['functions'][0]
                docstring = self.docstring_generator.generate_function_docstring(func)
                self.chat_area.append(f"\n<b>Example docstring for {func.name}:</b>\n{docstring}")
            
        except Exception as e:
            self.chat_area.append(f"<i>[Error generating docstrings: {e}]</i>")
    
    def explain_lint_errors(self):
        """Run linter and explain errors using AI"""
        if not hasattr(self, 'main_window'):
            self.chat_area.append("<i>[No main window attached]</i>")
            return
        
        try:
            editor = self.main_window.get_current_editor()
            if editor is None:
                self.chat_area.append("<i>[No active editor]</i>")
                return
            
            file_path = getattr(editor, 'file_path', None)
            if not file_path:
                self.chat_area.append("<i>[No file path available for linting]</i>")
                return
            
            self.chat_area.append("<b>Running code linter...</b>")
            errors = self.code_linter.lint_file(file_path)
            
            if not errors:
                self.chat_area.append("<i>[No errors found! Code looks good.]</i>")
                return
            
            self.chat_area.append(f"<b>Found {len(errors)} issues:</b>")
            
            for error in errors[:5]:
                self.chat_area.append(f"\n{error}")
                
                context = self.code_linter.get_error_context(file_path, error.line)
                if context:
                    self.chat_area.append(f"<pre>{context}</pre>")
            
            if len(errors) > 5:
                self.chat_area.append(f"\n<i>[... and {len(errors) - 5} more issues]</i>")
            
        except Exception as e:
            self.chat_area.append(f"<i>[Error running linter: {e}]</i>")
    
    def refactor_code(self, instruction: str):
        """Refactor code based on instruction"""
        if not hasattr(self, 'main_window'):
            return
        
        try:
            editor = self.main_window.get_current_editor()
            if editor is None:
                return
            
            if hasattr(editor, 'toPlainText'):
                code = editor.toPlainText()
            else:
                return
            
            prompt = f"""Refactor this Python code according to the instruction: {instruction}

Current code:
```python
{code}
```

Please provide the refactored code wrapped in <<<edit>>> tags.
"""
            
            if self.using_api and self.api_config:
                response = self.api_model_handler.generate_response(prompt)
            else:
                response = self.run_model(prompt)
            
            if self._contains_edit_tags(response):
                self.apply_response_to_editor(response)
                self.chat_area.append("<i>[Code refactored successfully]</i>")
            else:
                self.chat_area.append(f"<b>Refactoring suggestion:</b>\n{response}")
                
        except Exception as e:
            self.chat_area.append(f"<i>[Error refactoring code: {e}]</i>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AIEngine()
    widget.show()
    sys.exit(app.exec())
