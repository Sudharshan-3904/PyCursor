import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMenu,
    QTextEdit, QPushButton, QLineEdit, QInputDialog, QComboBox
)
from PyQt6.QtGui import QAction

from ..utils import load_icon
from .local_model_handler import LocalModelHandler


class AIAssistantWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.resize(600, 800)

        self.system_prompt = "You are a helpful AI assistant."
        self.chunk_size = 500  # characters per chunk

        # Load icons
        self.send_icon = load_icon("send.png")
        self.local_icon = load_icon("local.png")
        self.api_icon = load_icon("api.png")
        self.model_icon = load_icon("model.png")

        # Model storage
        self.models = self.detect_local_models()
        self.current_model_name = next(iter(self.models.keys()), None)
        self.current_backend = (
            "lmstudio" if self.current_model_name and self.current_model_name.startswith("LM Studio") else "ollama"
        )

        # Initialize local model handler
        self.local_model_handler = LocalModelHandler(
            backend=self.current_backend,
            model_name=self.current_model_name.split(": ", 1)[-1] if self.current_model_name else None
        )

        self.init_ui()


    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # ---------------- Chat Area ---------------- #
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        main_layout.addWidget(self.chat_area)

        # ---------------- Input Field ---------------- #
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.handle_send)
        main_layout.addWidget(self.input_field)

        # ---------------- Toolbar ---------------- #
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)

        # API/Local toggle button
        self.using_api = False  # default to local
        self.api_local_btn = QPushButton()
        self.api_local_btn.setIcon(self.local_icon)
        self.api_local_btn.setCheckable(True)
        self.api_local_btn.setFixedHeight(28)
        self.api_local_btn.clicked.connect(self.toggle_api_local)
        toolbar_layout.addWidget(self.api_local_btn)

        # Model selection button
        self.model_btn = QPushButton()
        self.model_btn.setIcon(self.model_icon)
        self.model_btn.setFixedHeight(28)
        self.model_btn.setToolTip("Select AI Model")

        # Create a QMenu for the button
        self.model_menu = QMenu(self)
        self.populate_model_menu()
        self.model_btn.setMenu(self.model_menu)

        toolbar_layout.addWidget(self.model_btn)

        # Stretch / free space
        toolbar_layout.addStretch()

        # Send button
        self.send_btn = QPushButton()
        self.send_btn.setIcon(self.send_icon)
        self.send_btn.setFixedHeight(28)
        self.send_btn.setToolTip("Send message")
        self.send_btn.clicked.connect(self.handle_send)
        toolbar_layout.addWidget(self.send_btn)

        main_layout.addLayout(toolbar_layout)
        self.setLayout(main_layout)

    # ---------------- MODEL MENU ---------------- #
    def populate_model_menu(self):
        self.model_menu.clear()

        # LM Studio models
        lm_studio_models = [name for name in self.models if name.startswith("LM Studio")]
        if lm_studio_models:
            for model in lm_studio_models:
                action = QAction(model.split(": ", 1)[-1], self)
                # capture the full model name in lambda default argument
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)
            self.model_menu.addSeparator()

        # Ollama models
        ollama_models = [name for name in self.models if name.startswith("Ollama")]
        if ollama_models:
            for model in ollama_models:
                action = QAction(model.split(": ", 1)[-1], self)
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)
            self.model_menu.addSeparator()

        # API models (static example)
        api_models = ["chat gpt go"]
        for model in api_models:
            action = QAction(model, self)
            action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
            self.model_menu.addAction(action)

    # ---------------- MODEL CHANGE HANDLER ---------------- #
    def on_model_change(self, selected_model):
        if selected_model:
            self.current_model_name = selected_model
            self.current_backend = "lmstudio" if selected_model.startswith("LM Studio") else "ollama"
            self.local_model_handler = LocalModelHandler(
                backend=self.current_backend,
                model_name=selected_model.split(": ", 1)[-1]
            )
            self.chat_area.append(f"<i>[Model switched to: {self.current_model_name}]</i>")

    # ---------------- MODEL SELECTION ---------------- #
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
            # Update the handler
            self.local_model_handler = LocalModelHandler(
                backend=self.current_backend,
                model_name=item.split(": ", 1)[-1]
            )
            self.chat_area.append(f"<i>[Model switched to: {self.current_model_name}]</i>")

    # Toggle method
    def toggle_api_local(self):
        self.using_api = self.api_local_btn.isChecked()
        if self.using_api:
            self.api_local_btn.setIcon(self.api_icon)
            self.api_local_btn.setToolTip("Using API models")
        else:
            self.api_local_btn.setIcon(self.local_icon)
            self.api_local_btn.setToolTip("Using Local models")

    # ---------------- MODEL DETECTION ---------------- #
    def detect_local_models(self):
        models = {}

        # LM Studio
        lm_studio_path = os.path.expanduser("~/.lmstudio/models")
        if os.path.exists(lm_studio_path):
            for model in os.listdir(lm_studio_path):
                models[f"LM Studio: {model}"] = os.path.join(lm_studio_path, model)

        # Ollama
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.strip():
                    models[f"Ollama: {line.strip()}"] = line.strip()
        except Exception as e:
            print("Ollama detection failed:", e)

        return models

    # ---------------- SEND HANDLER ---------------- #
    def handle_send(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.chat_area.append(f"<b>User:</b> {user_input}")
        self.input_field.clear()

        # In handle_send():
        if self.using_api:
            # API placeholder
            model_identifier = next(iter(self.models.values()), "default")
            response = self.api_model_response(user_input, model_identifier)
        else:
            # Local model
            response = self.local_model_handler.local_model_response(user_input)

        self.chat_area.append(f"<b>AI:</b> {response}\n")
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def api_model_response(self, prompt, model_identifier):
        return f"[API response from {model_identifier}]"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AIAssistantWidget()
    widget.show()
    sys.exit(app.exec())
