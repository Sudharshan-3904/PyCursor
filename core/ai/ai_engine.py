import requests
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

        # Initialize local model handler first
        self.local_model_handler = LocalModelHandler()

        # Model storage
        self.models = self.local_model_handler.detect_models()
        self.current_model_name = next(iter(self.models.keys()), None)
        self.current_backend = (
            "lmstudio" if self.current_model_name and self.current_model_name.startswith("LM Studio") else "ollama"
        )

        # Detect models via the handler
        self.models = self.local_model_handler.detect_models()

        # Pick first model if available
        self.current_model_name = next(iter(self.models.keys()), None)
        self.current_backend = (
            "lmstudio" if self.current_model_name and self.current_model_name.startswith("LM Studio") else "ollama"
        )

        # Update handler with actual model
        self.local_model_handler.backend = self.current_backend
        self.local_model_handler.model_name = (
            self.current_model_name.split(": ", 1)[-1] if self.current_model_name else None
        )

        self.using_api = False  # default to local

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

        # Model menu
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

        # Add toolbar to main layout
        main_layout.addLayout(toolbar_layout)

        self.setLayout(main_layout)

    # ---------------- MODEL MENU ---------------- #
    def populate_model_menu(self):
        self.model_menu.clear()

        # LM Studio models
        lm_studio_models = [name for name in self.models if name.startswith("LM Studio")]
        if lm_studio_models:
            # Add a non-clickable section header
            lm_studio_header = QAction("LM Studio models", self)
            lm_studio_header.setEnabled(False)
            self.model_menu.addAction(lm_studio_header)

            for model in lm_studio_models:
                action = QAction(model.split(": ", 1)[-1], self)  # just the name after "LM Studio: "
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)
            self.model_menu.addSeparator()

        # Ollama models
        ollama_models = [name for name in self.models if name.startswith("Ollama")]
        if ollama_models:
            ollama_header = QAction("Ollama models", self)
            ollama_header.setEnabled(False)
            self.model_menu.addAction(ollama_header)

            for model in ollama_models:
                action = QAction(model.split(": ", 1)[-1], self)  # just the name after "Ollama: "
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)
            self.model_menu.addSeparator()

        # API models (static example)
        api_models = ["chat gpt go"]
        if api_models:
            api_header = QAction("API models", self)
            api_header.setEnabled(False)
            self.model_menu.addAction(api_header)

            for model in api_models:
                action = QAction(model, self)
                action.triggered.connect(lambda checked=False, m=model: self.on_model_change(m))
                self.model_menu.addAction(action)

    # ---------------- MODEL CHANGE HANDLER ---------------- #
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

        # Update the same handler
        self.local_model_handler.backend = backend
        self.local_model_handler.model_name = model_identifier

        self.chat_area.append(f"<i>[Switched to {backend} model: {model_identifier}]</i>")

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
