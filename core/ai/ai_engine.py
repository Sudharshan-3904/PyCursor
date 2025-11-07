# ai_engine.py
import asyncio
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import pyqtSignal
import openai

# Optional: Hugging Face Transformers for local LLM
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False

class AIEngine(QWidget):
    """AI Engine Widget for PyCursor
    Supports both Local LLMs and API-based LLMs.
    Emits 'response_ready' signal when AI response is ready.
    """
    
    response_ready = pyqtSignal(str)

    def __init__(self, api_key: str = None, local_model_name: str = None, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.local_model_name = local_model_name

        # Initialize layout
        self.layout = QVBoxLayout()
        self.input_box = QTextEdit()
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.ask_button = QPushButton("Ask AI")
        self.ask_button.clicked.connect(lambda: asyncio.create_task(self.ask_ai()))

        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.ask_button)
        self.layout.addWidget(self.output_box)
        self.setLayout(self.layout)

        # Setup OpenAI API if key is provided
        if self.api_key:
            openai.api_key = self.api_key

        # Setup local LLM if available and specified
        if LOCAL_LLM_AVAILABLE and self.local_model_name:
            self._setup_local_model(self.local_model_name)
        else:
            self.local_generator = None

    def _setup_local_model(self, model_name):
        """Initialize local Hugging Face model"""
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
        self.local_generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

    async def ask_ai(self, use_local: bool = False):
        """Ask AI either via API or local model"""
        prompt = self.input_box.toPlainText().strip()
        if not prompt:
            self.output_box.setText("Please enter a prompt.")
            return

        self.output_box.setText("Thinking...")

        if use_local and self.local_generator:
            # Run local LLM in a thread to avoid blocking
            response = await asyncio.to_thread(self._ask_local, prompt)
        elif self.api_key:
            # Run API call in a thread to avoid blocking
            response = await asyncio.to_thread(self._ask_api, prompt)
        else:
            response = "No AI model available. Provide API key or local model."

        self.output_box.setText(response)
        self.response_ready.emit(response)

    def _ask_api(self, prompt: str) -> str:
        """Query OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"API Error: {e}"

    def _ask_local(self, prompt: str) -> str:
        """Query local LLM"""
        try:
            result = self.local_generator(prompt, max_length=200, do_sample=True)
            return result[0]['generated_text'].strip()
        except Exception as e:
            return f"Local LLM Error: {e}"

# Example usage (for testing only)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ai_widget = AIEngine(api_key="YOUR_OPENAI_API_KEY", local_model_name="TheBloke/LLaMA-3B-GPTQ")
    ai_widget.show()
    sys.exit(app.exec())
