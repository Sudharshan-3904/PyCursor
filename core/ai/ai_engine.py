import sys
import os
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMenu,
    QTextEdit, QPushButton, QLineEdit, QInputDialog
)
from PyQt6.QtGui import QAction

from ..utils import load_icon
from .local_model_handler import LocalModelHandler


class AIEngine(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.resize(600, 800)

        self.system_prompt = "You are a helpful AI assistant."
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

        self.models = self.local_model_handler.detect_models()

        self.current_model_name = next(iter(self.models.keys()), None)
        self.current_backend = (
            "lmstudio" if self.current_model_name and self.current_model_name.startswith("LM Studio") else "ollama"
        )

        self.local_model_handler.backend = self.current_backend
        self.local_model_handler.model_name = (
            self.current_model_name.split(": ", 1)[-1] if self.current_model_name else None
        )

        self.using_api = False

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        main_layout.addWidget(self.chat_area)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.handle_send)
        main_layout.addWidget(self.input_field)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)

        self.api_local_btn = QPushButton()
        self.api_local_btn.setIcon(self.local_icon)
        self.api_local_btn.setCheckable(True)
        self.api_local_btn.setFixedHeight(28)
        self.api_local_btn.clicked.connect(self.toggle_api_local)
        toolbar_layout.addWidget(self.api_local_btn)

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

    def handle_send(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"<b>User:</b> {user_input}")
        self.input_field.clear()

        if self.using_api:
            model_identifier = next(iter(self.models.values()), "default")
            response = self.api_model_response(user_input, model_identifier)
        else:
            response = self.local_model_handler.local_model_response(user_input)

        self.chat_area.append(f"<b>AI:</b> {response}\n")
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def api_model_response(self, prompt, model_identifier):
        return f"[API response from {model_identifier}]"
    
    
    def set_main_window(self, main_window):
        """Provide a reference to the main application window so AI can modify files / notify."""
        self.main_window = main_window

    def run_model(self, prompt: str) -> str:
        """
        Unified entry for gathering full LLM response.
        Accepts either:
          - a full string response, or
          - an iterable/generator yielding chunks (streaming)
        This will collect the entire response and return it as a single string.
        """
        try:
            # Try getting a response from local handler
            resp = self.local_model_handler.local_model_response(prompt)

            # If response is already a string, return it
            if isinstance(resp, str):
                return resp

            # If response is iterable (streaming chunks), join them
            if hasattr(resp, "__iter__") and not isinstance(resp, (dict, bytes)):
                collected = []
                for chunk in resp:
                    try:
                        collected.append(str(chunk))
                    except Exception:
                        # best-effort append
                        collected.append(repr(chunk))
                return "".join(collected)

            # Fallback: stringify whatever we got
            return str(resp)
        except TypeError:
            # If local_model_response signature is different, try calling without args returned above
            try:
                return str(self.local_model_handler.local_model_response(prompt))
            except Exception as e:
                return f"[AI Error] {e}"
        except Exception as e:
            return f"[AI Error] {e}"

    def _contains_edit_tags(self, response: str) -> bool:
        """Check if response contains edit tags indicating file modification."""
        return "<<<edit>>>" in response and "<</edit>>" in response

    def handle_send(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"<b>User:</b> {user_input}")
        self.input_field.clear()

        if self.using_api:
            # keep existing behaviour for API placeholder
            model_identifier = next(iter(self.models.values()), "default")
            response = self.api_model_response(user_input, model_identifier)
        else:
            # Use unified run_model to collect full response (supports streaming or full-string)
            response = self.run_model(user_input)

        # Append to chat area
        self.chat_area.append(f"<b>AI:</b> {response}\n")
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

        # Only apply to editor if response contains edit tags (file modification intent)
        if self._contains_edit_tags(response):
            try:
                self.apply_response_to_editor(response)
            except Exception as e:
                # non-fatal; show in chat area for debugging
                self.chat_area.append(f"<i>[Failed to apply response to file: {e}]</i>")
        # If no edit tags, response is treated as a Q&A answer and stays in chat area

    def apply_response_to_editor(self, response: str):
        """
        Extract content from edit tags and apply to the currently open file (or create a new one).
        Expects format: <<<edit>>>content here<</edit>>
        After modification, notify the main window with the number of lines added.
        """
        # Extract content between edit tags
        edit_start = response.find("<<<edit>>>")
        edit_end = response.find("<</edit>>")
        
        if edit_start != -1 and edit_end != -1:
            # Extract content between tags
            edit_start += len("<<<edit>>>")
            extracted_content = response[edit_start:edit_end].strip()
        else:
            # No tags found, use entire response
            extracted_content = response
        
        if not extracted_content:
            # No content to write
            self.chat_area.append(f"<i>[No content to write to file]</i>")
            return

        if not hasattr(self, "main_window") or self.main_window is None:
            # No main window linked: create file in cwd
            project_root = os.getcwd()
            filename = f"ai_output_{int(time.time())}.txt"
            full_path = os.path.join(project_root, filename)

            with open(full_path, "a", encoding="utf-8") as f:
                before_lines = 0
                f.write(extracted_content if extracted_content.endswith("\n") else extracted_content + "\n")
                added_lines = len(extracted_content.splitlines())
            # Can't notify UI, but append a notice to chat
            self.chat_area.append(f"<i>[Wrote {added_lines} lines to {filename}]</i>")
            return

        # Get current editor widget from main window
        editor = None
        try:
            editor = self.main_window.get_current_editor()
        except Exception:
            editor = None

        if editor is None:
            # No open editor -> create new file in project root
            project_root = getattr(self.main_window, "project_path", os.getcwd())
            filename = f"ai_output_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.py"
            full_path = os.path.join(project_root, filename)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(extracted_content if extracted_content.endswith("\n") else extracted_content + "\n")
            added_lines = len(extracted_content.splitlines())
            # Notify main window UI
            try:
                self.main_window.notify_lines_added(filename, added_lines)
            except Exception:
                self.chat_area.append(f"<i>[Created {filename} ({added_lines} lines)]</i>")
            return

        # If editor has an associated file path, append there. Otherwise create a new untitled file/tab.
        file_path = getattr(editor, "file_path", None)
        if file_path:
            try:
                # Get current editor content
                current_content = editor.toPlainText()
                
                # Append extracted content to current content
                if current_content and not current_content.endswith("\n"):
                    new_content = current_content + "\n" + extracted_content
                else:
                    new_content = current_content + extracted_content
                
                # Ensure it ends with newline
                if not new_content.endswith("\n"):
                    new_content += "\n"
                
                # Write entire content to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                # Update editor widget with new content
                editor.setPlainText(new_content)
                
                # Count added lines
                added_lines = len(extracted_content.splitlines())

                # Notify main window UI
                self.main_window.notify_lines_added(os.path.basename(file_path), added_lines)
            except Exception as e:
                raise
        else:
            # Editor has no file path -> create a new file and load it as a new tab if main_window supports it
            project_root = getattr(self.main_window, "project_path", os.getcwd())
            filename = f"ai_output_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.py"
            full_path = os.path.join(project_root, filename)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(extracted_content if extracted_content.endswith("\n") else extracted_content + "\n")
            added_lines = len(extracted_content.splitlines())
            # Ask main window to open this file if it has such method
            if hasattr(self.main_window, "open_file_in_tab"):
                self.main_window.open_file_in_tab(full_path)
            self.main_window.notify_lines_added(filename, added_lines)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AIEngine()
    widget.show()
    sys.exit(app.exec())
