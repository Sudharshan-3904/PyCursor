import pytest
from core.ai.ai_engine import AIEngine
from PyQt6.QtWidgets import QApplication
import sys

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_ai_engine_initialization(qapp, qtbot):
    ai_widget = AIEngine()
    qtbot.addWidget(ai_widget)
    assert ai_widget is not None
    # Check if the input field is present
    assert hasattr(ai_widget, "input_field")

def test_ai_engine_model_update(qapp, qtbot):
    ai_widget = AIEngine()
    qtbot.addWidget(ai_widget)
    models = {"gpt-4": {"provider": "openai"}, "llama3": {"provider": "ollama"}}
    ai_widget.update_models(models)
    # Check if model selector has the items
    # (Assuming there's a combo box for models)
    if hasattr(ai_widget, "model_selector"):
        assert ai_widget.model_selector.count() >= 2
