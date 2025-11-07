# core/ui/ai_widget.py
from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt
import os

class AIAssistantWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(5,5,5,5)

        # --- Prompt input box ---
        self.prompt_box = QTextEdit()
        self.prompt_box.setPlaceholderText("Type a prompt here and press 'Send'...")
        self.layout().addWidget(self.prompt_box)

        # --- Bottom controls: Send + selectors ---
        controls_layout = QHBoxLayout()

        # Left selector: Local / API
        self.local_api_btn = QPushButton()
        self.local_api_btn.setIcon(self.load_icon("local.png"))
        self.local_api_btn.setIconSize(QSize(24,24))
        self.local_api_btn.setFixedSize(32,32)
        self.local_api_btn.setToolTip("Toggle Local/API Execution")
        controls_layout.addWidget(self.local_api_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Spacer for Send button
        controls_layout.addStretch(1)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedHeight(32)
        controls_layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer for right selector
        controls_layout.addStretch(1)

        # Right selector: Model selection
        self.model_btn = QPushButton()
        self.model_btn.setIcon(self.load_icon("model.png"))
        self.model_btn.setIconSize(QSize(24,24))
        self.model_btn.setFixedSize(32,32)
        self.model_btn.setToolTip("Select Model")
        controls_layout.addWidget(self.model_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout().addLayout(controls_layout)

        # --- Connections ---
        self.send_btn.clicked.connect(self.send_prompt)
        self.local_api_btn.clicked.connect(self.toggle_execution_mode)
        self.model_btn.clicked.connect(self.choose_model)

        # State
        self.execution_mode = "API"  # or "Local"
        self.current_model = "LLaMA-3"

    def load_icon(self, filename):
        base_dir = os.path.join(os.path.dirname(__file__), "../../assets/icons")
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            return QIcon(QPixmap(path))
        return QIcon()

    def send_prompt(self):
        prompt = self.prompt_box.toPlainText().strip()
        if not prompt:
            return
        print(f"[AI] Sending prompt using {self.execution_mode}, model {self.current_model}: {prompt}")
        # TODO: call LLM engine here

    def toggle_execution_mode(self):
        self.execution_mode = "Local" if self.execution_mode == "API" else "API"
        print(f"[AI] Execution mode switched to {self.execution_mode}")

    def choose_model(self):
        # Here you could pop up a menu or cycle through models
        # For demo, we just toggle between two
        self.current_model = "Mistral" if self.current_model == "LLaMA-3" else "LLaMA-3"
        print(f"[AI] Model changed to {self.current_model}")
