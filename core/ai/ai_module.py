from __future__ import annotations
import os
from dataclasses import dataclass
from difflib import SequenceMatcher, unified_diff
from typing import List, Tuple

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont, QFontDatabase, QFontInfo
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QSplitter, QTextEdit, QVBoxLayout, QWidget,
    QCheckBox, QScrollArea, QSizePolicy
)

from .api_model_handler import APIModelHandler, APIConfig

class LLMClient:
    """
    Standardized client for LLM interactions within the AI Module.
    Wraps APIModelHandler to provide high-level methods for code editing and Q&A.
    """
    def __init__(self, config: dict):
        self.handler = APIModelHandler()
        provider = config.get("provider", "openai")
        self.handler.configure(provider=provider)

    def request_code_edit(self, filename: str, full_code: str, instruction: str) -> dict:
        prompt = f"File: {filename}\n\nCode:\n```python\n{full_code}\n```\n\nInstruction: {instruction}\n\nRespond with a JSON object: {{'modified_code': '...', 'explanation': '...'}}"
        response = self.handler.generate_response(prompt)
        # Simple JSON extraction logic (could be more robust)
        try:
            import json
            # Find JSON block in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception:
            pass
        return {"modified_code": response, "explanation": "Direct response applied."}

    def answer_question(self, filename: str, full_code: str, question: str) -> dict:
        prompt = f"File: {filename}\n\nCode:\n```python\n{full_code}\n```\n\nQuestion: {question}"
        response = self.handler.generate_response(prompt)
        return {"answer": response}

def on_suggestion_ready(window, result: dict):
    """
    Callback for AI suggestions. Now accepts the parent window as an argument.
    """
    modified = result.get("modified_code", "")
    explanation = result.get("explanation", "")
    original = get_editor_full_text_generic(window.editor_tabs.currentWidget())

    if not modified.strip() or modified == "{}":
        QMessageBox.warning(window, "Empty AI Response", "The AI returned no code.")
        return

    if modified.strip() == original.strip():
        window.statusBar().showMessage("No changes from AI", 3000)
        return

    try:
        dialog = AISuggestionDialog(window, original, modified, explanation)
        if dialog.exec():
            # Apply changes (full replacement for now if hunks aren't used)
            set_editor_full_text_generic(window.editor_tabs.currentWidget(), modified)
            window.statusBar().showMessage("AI suggestion applied", 3000)
    except Exception as e:
        QMessageBox.critical(window, "AI Apply Error", str(e))


class _LLMWorker(QThread):
    finished_with_result = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, llm_client: LLMClient, mode: str, filename: str, full_code: str, payload: str):
        super().__init__()
        self.llm_client = llm_client
        self.mode = mode
        self.filename = filename
        self.full_code = full_code
        self.payload = payload

    def run(self):
        try:
            if self.mode == "edit":
                result = self.llm_client.request_code_edit(self.filename, self.full_code, self.payload)
            elif self.mode == "qa":
                result = self.llm_client.answer_question(self.filename, self.full_code, self.payload)
            else:
                raise RuntimeError(f"Unknown worker mode: {self.mode}")
            
            if not isinstance(result, dict):
                raise RuntimeError("LLM did not return a valid dictionary.")
            self.finished_with_result.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class AIManager(QWidget):
    suggestion_ready = pyqtSignal(dict)
    suggestion_failed = pyqtSignal(str)
    qa_ready = pyqtSignal(dict)
    qa_failed = pyqtSignal(str)

    def __init__(self, llm_client: LLMClient):
        super().__init__()
        self.llm_client = llm_client
        self._workers: List[_LLMWorker] = []

    def request_suggestion(self, filename: str, full_code: str, instruction: str):
        w = _LLMWorker(self.llm_client, "edit", filename, full_code, instruction)
        w.finished_with_result.connect(self._on_suggestion_finished)
        w.failed.connect(self._on_suggestion_failed)
        self._workers.append(w)
        w.start()

    def request_qa(self, filename: str, full_code: str, question: str):
        w = _LLMWorker(self.llm_client, "qa", filename, full_code, question)
        w.finished_with_result.connect(self._on_qa_finished)
        w.failed.connect(self._on_qa_failed)
        self._workers.append(w)
        w.start()

    def _on_suggestion_finished(self, result: dict):
        self.suggestion_ready.emit(result)

    def _on_suggestion_failed(self, message: str):
        self.suggestion_failed.emit(message)

    def _on_qa_finished(self, result: dict):
        self.qa_ready.emit(result)

    def _on_qa_failed(self, message: str):
        self.qa_failed.emit(message)


@dataclass
class DiffHunk:
    hunk_id: int
    old_start: int
    old_end: int
    new_text: str
    header: str


def _compute_unified_diff(old: str, new: str) -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff_lines = list(unified_diff(old_lines, new_lines, fromfile='a', tofile='b'))
    return ''.join(diff_lines)

def compute_hunks(old: str, new: str) -> List[DiffHunk]:
    sm = SequenceMatcher(None, old, new)
    hunks: List[DiffHunk] = []
    hunk_counter = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        replacement = new[j1:j2]
        header = f"@@ -{i1},{i2-i1} +{j1},{j2-j1} @@"
        hunks.append(DiffHunk(hunk_id=hunk_counter, old_start=i1, old_end=i2, new_text=replacement, header=header))
        hunk_counter += 1
    return hunks

def get_editor_full_text_generic(editor) -> str:
    if hasattr(editor, "text") and callable(getattr(editor, "text")):
        try:
            return editor.text()
        except Exception:
            pass
    if hasattr(editor, "toPlainText") and callable(getattr(editor, "toPlainText")):
        return editor.toPlainText()
    return str(editor)

def set_editor_full_text_generic(editor, new_text: str):
    if hasattr(editor, "setText") and callable(getattr(editor, "setText")):
        try:
            editor.setText(new_text)
            return
        except Exception:
            pass
    if hasattr(editor, "setPlainText") and callable(getattr(editor, "setPlainText")):
        editor.setPlainText(new_text)
        return
    raise RuntimeError("Unable to set editor text: unsupported editor widget")

def _char_index_to_line_col(text: str, char_idx: int) -> Tuple[int, int]:
    if char_idx <= 0:
        return 0, 0
    upto = text[:char_idx]
    line = upto.count("\n")
    if line == 0:
        col = len(upto)
    else:
        last_nl = upto.rfind("\n")
        col = len(upto) - last_nl - 1
    return line, col

def apply_selected_hunks(editor, hunks: List[DiffHunk]):
    if not hunks:
        return

    is_qsci = hasattr(editor, "setSelection") and hasattr(editor, "replaceSelectedText")

    try:
        full_text = get_editor_full_text_generic(editor)
    except Exception:
        full_text = ""

    for h in sorted(hunks, key=lambda x: x.old_start, reverse=True):
        if is_qsci:
            start_line, start_col = _char_index_to_line_col(full_text, h.old_start)
            end_line, end_col = _char_index_to_line_col(full_text, h.old_end)
            try:
                editor.setSelection(start_line, start_col, end_line, end_col)
                editor.replaceSelectedText(h.new_text)
            except Exception as e:
                new_full = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
                set_editor_full_text_generic(editor, new_full)
                full_text = new_full
                continue
            full_text = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
        else:
            try:
                doc = editor.document()
                cursor = QTextCursor(doc)
                cursor.setPosition(h.old_start)
                cursor.setPosition(h.old_end, QTextCursor.MoveMode.KeepAnchor)
                cursor.beginEditBlock()
                cursor.insertText(h.new_text)
                cursor.endEditBlock()
                full_text = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
            except Exception:
                new_full = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
                set_editor_full_text_generic(editor, new_full)
                full_text = new_full


class HunkWidget(QWidget):
    def __init__(self, hunk: DiffHunk, old_excerpt: str, parent=None):
        super().__init__(parent)
        self.hunk = hunk
        self.checkbox = QCheckBox(f"Hunk {hunk.hunk_id}: {hunk.header}")
        self.checkbox.setChecked(True)
        self.old_view = QTextEdit()
        self.old_view.setReadOnly(True)
        self.old_view.setPlainText(old_excerpt)
        self.new_view = QTextEdit()
        self.new_view.setReadOnly(True)
        self.new_view.setPlainText(hunk.new_text)
        
        # Set font to prevent invalid font sizes
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            font = QFont("Courier New", 10)
            font.setPointSize(10)
        self.old_view.setFont(font)
        self.new_view.setFont(font)
        s = QSplitter(Qt.Orientation.Horizontal)
        s.addWidget(self.old_view)
        s.addWidget(self.new_view)
        s.setSizes([200, 200])
        layout = QVBoxLayout(self)
        layout.addWidget(self.checkbox)
        layout.addWidget(s)

    def is_accepted(self) -> bool:
        return self.checkbox.isChecked()


class AISuggestionDialog(QDialog):
    def __init__(self, parent, original: str, modified: str, explanation: str = ""):
        super().__init__(parent)
        self.setWindowTitle("AI Code Suggestions — Preview & Apply")
        self.resize(1000, 700)
        self._original = original
        self._modified = modified
        layout = QVBoxLayout(self)
        # Define font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            font = QFont("Courier New", 10)
            font.setPointSize(10)
        if explanation:
            label = QLabel(f"<b>Explanation:</b><br>{explanation}")
            label.setWordWrap(True)
            layout.addWidget(label)
        diff_text = _compute_unified_diff(original, modified)
        diff_label = QLabel("<b>Unified diff (overview):</b>")
        layout.addWidget(diff_label)
        diff_view = QTextEdit()
        diff_view.setReadOnly(True)
        diff_view.setPlainText(diff_text)
        diff_view.setFixedHeight(180)
        
        # Set font
        diff_view.setFont(font)
        
        layout.addWidget(diff_view)
        self.hunk_widgets: List[HunkWidget] = []
        hunks = compute_hunks(original, modified)
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        for h in hunks:
            old_excerpt = original[h.old_start:h.old_end]
            hw = HunkWidget(h, old_excerpt)
            self.hunk_widgets.append(hw)
            scroll_layout.addWidget(hw)
        if not self.hunk_widgets:
            layout.addWidget(QLabel("No changes were proposed by the AI."))
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(scroll)
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply accepted hunks")
        self.apply_all_btn = QPushButton("Accept all & apply")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.apply_all_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.apply_btn.clicked.connect(self.accept)
        self.apply_all_btn.clicked.connect(self._accept_all_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _accept_all_and_accept(self):
        for hw in self.hunk_widgets:
            hw.checkbox.setChecked(True)
        self.accept()

    def accepted_hunks(self) -> List[DiffHunk]:
        return [hw.hunk for hw in self.hunk_widgets if hw.is_accepted()]


class QAResponseDialog(QDialog):
    def __init__(self, parent, question: str, answer: str):
        super().__init__(parent)
        self.setWindowTitle("AI Answer")
        self.resize(700, 400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Question:</b><br>{question}"))
        # Define font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            font = QFont("Courier New", 10)
            font.setPointSize(10)
        ans_view = QTextEdit()
        ans_view.setReadOnly(True)
        ans_view.setPlainText(answer)
        
        # Set font
        ans_view.setFont(font)
        
        layout.addWidget(ans_view)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


def install_ai_actions(window):
    llm_client = LLMClient(config={"provider": "openai" if _HAS_OPENAI and os.getenv("OPENAI_API_KEY") else "stub"})
    ai_manager = AIManager(llm_client)