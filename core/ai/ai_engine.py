from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from functools import partial
import os
import requests

from langchain_ollama import ChatOllama
from core.utils import load_icon


class AIAssistantWidget(QWidget):
    LOCAL_MODE_ICON = "local.png"
    API_MODE_ICON = "api.png"

    def __init__(self, local_models_dir=None):
        super().__init__()

        self.local_models_dir = local_models_dir or os.path.join(os.path.expanduser("~"), "ai_models")
        self.execution_mode = "API"

        # Detect models upfront (synchronously)
        self.available_models = self.detect_all_models()
        self.current_model = self.available_models[0] if self.available_models else "LLaMA-3"

        # --------------------------
        # Layout
        # --------------------------
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)

        # Prompt box
        self.prompt_box = QTextEdit()
        self.prompt_box.setPlaceholderText("Type a prompt here and press 'Send'...")
        self.layout().addWidget(self.prompt_box)

        # Controls
        controls_layout = QHBoxLayout()

        # Local/API button
        self.local_api_btn = QPushButton()
        self.update_execution_icon()
        self.local_api_btn.setIconSize(QSize(32, 32))
        self.local_api_btn.setFixedSize(36, 36)
        self.local_api_btn.setToolTip(f"Execution Mode: {self.execution_mode}")
        controls_layout.addWidget(self.local_api_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Spacer
        controls_layout.addStretch(1)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedHeight(32)
        controls_layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer
        controls_layout.addStretch(1)

        # Model button
        self.model_btn = QPushButton()
        self.model_btn.setIcon(load_icon("model.png", recolor_to_white=True))
        self.model_btn.setIconSize(QSize(32, 32))
        self.model_btn.setFixedSize(36, 36)
        self.model_btn.setToolTip(f"Model: {self.current_model}")
        controls_layout.addWidget(self.model_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout().addLayout(controls_layout)

        # --------------------------
        # Signals
        # --------------------------
        self.send_btn.clicked.connect(self.send_prompt)
        self.local_api_btn.clicked.connect(self.toggle_execution_mode)
        self.model_btn.clicked.connect(self.show_model_menu)

    # --------------------------
    # Execution mode
    # --------------------------
    def update_execution_icon(self):
        icon_file = self.LOCAL_MODE_ICON if self.execution_mode == "Local" else self.API_MODE_ICON
        self.local_api_btn.setIcon(load_icon(icon_file))
        self.local_api_btn.setToolTip(f"Execution Mode: {self.execution_mode}")

    def toggle_execution_mode(self):
        self.execution_mode = "Local" if self.execution_mode == "API" else "API"
        self.update_execution_icon()
        print(f"[AI] Execution mode switched to {self.execution_mode}")

    # --------------------------
    # Model detection
    # --------------------------
    def detect_ollama_models(self):
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

    def detect_lm_studio_models(self):
        try:
            r = requests.get("http://localhost:1234/v1/models", timeout=2)
            r.raise_for_status()
            return [m["id"] for m in r.json().get("data", [])]
        except Exception:
            return []

    def detect_local_models(self):
        models = []
        if os.path.exists(self.local_models_dir):
            for folder in os.listdir(self.local_models_dir):
                folder_path = os.path.join(self.local_models_dir, folder)
                if os.path.isdir(folder_path):
                    models.append(folder)
        return models or ["LLaMA-3", "Mistral"]

    def detect_all_models(self):
        """Return combined list of all available models."""
        return self.detect_ollama_models() + self.detect_lm_studio_models() + self.detect_local_models()

    # --------------------------
    # Model menu
    # --------------------------
    def show_model_menu(self):
        menu = QMenu(self)

        sections = [
            ("Ollama", self.detect_ollama_models()),
            ("LM Studio", self.detect_lm_studio_models()),
            ("Local/Fallback", self.detect_local_models())
        ]

        first_section = True
        for title, models in sections:
            if not models:
                continue
            if not first_section:
                menu.addSeparator()
            first_section = False

            for model in models:
                action = menu.addAction(model)
                action.triggered.connect(partial(self.set_model, model))
                if model == self.current_model:
                    action.setCheckable(True)
                    action.setChecked(True)

        menu.popup(self.model_btn.mapToGlobal(self.model_btn.rect().bottomLeft()))

    def set_model(self, model_name):
        self.current_model = model_name
        self.model_btn.setToolTip(f"Model: {self.current_model}")
        print(f"[AI] Model changed to {self.current_model}")

    # --------------------------
    # AI engine
    # --------------------------
    def ai_engine(self, prompt: str) -> str:
        if self.execution_mode == "API":
            return f"[API response] Prompt: {prompt}"

        response_text = ""
        if self.current_model in self.detect_ollama_models():
            try:
                client = ChatOllama(model=self.current_model)
                response_text = client.predict(prompt)
            except Exception as e:
                response_text = f"[Ollama error] {e}"
        elif self.current_model in self.detect_lm_studio_models():
            try:
                url = "http://localhost:1234/v1/completions"
                payload = {"model": self.current_model, "prompt": prompt, "max_tokens": 256}
                r = requests.post(url, json=payload)
                r.raise_for_status()
                response_text = r.json()["choices"][0]["text"]
            except Exception as e:
                response_text = f"[LM Studio error] {e}"
        else:
            response_text = f"[Local model '{self.current_model}' not found]"

        return response_text

    def send_prompt(self):
        prompt = self.prompt_box.toPlainText().strip()
        if not prompt:
            return
        print(f"[AI] Sending prompt using {self.execution_mode}, model {self.current_model}: {prompt}")
        response = self.ai_engine(prompt)
        print(f"[AI] Response: {response}")
