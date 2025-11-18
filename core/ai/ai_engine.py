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

    def api_model_response(self, prompt, model_identifier):
        return f"[API response from {model_identifier}]"
    
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

        if self.using_api:
            model_identifier = next(iter(self.models.values()), "default")
            response = self.api_model_response(user_input, model_identifier)
        else:
            response = self.run_model(user_input)

        print("Model Response:", response)

        if self._contains_edit_tags(response):
            try:
                self.apply_response_to_editor(response)
                self.chat_area.append("<i>[AI wrote changes to the editor]</i>")
            except Exception as e:
                self.chat_area.append(f"<i>[Failed to apply response to editor: {e}]</i>")
            return

        self.chat_area.append(f"<b>AI:</b> {response}\n")
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def apply_response_to_editor(self, response: str):
        print("Full AI Response:\n", repr(response))

        if "<<<edit>>>" in response and "<<</edit>>>" in response:
            start = response.find("<<<edit>>>") + len("<<<edit>>>")
            end = response.find("<<</edit>>>")

            extracted = response[start:end].strip()
            print("Extracted Code to Apply:\n", repr(extracted))
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

        print("New Content to Apply to Editor:\n", repr(new_content))

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AIEngine()
    widget.show()
    sys.exit(app.exec())
