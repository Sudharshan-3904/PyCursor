# core/ai/ai_module.py
"""
Single-file AI integration for PyCursor with:
 - LLMClient (OpenAI or stub)
 - AIManager (worker threads)
 - edit flow (per-hunk preview + accept/reject)
 - QA flow (ask questions about the open file)
 - install_ai_actions(window) helper to wire into MainWindow

Usage:
 - put this file at core/ai/ai_module.py
 - import install_ai_actions in your MainWindow and call it after editor init:
     from core.ai.ai_module import install_ai_actions
     install_ai_actions(self)
"""

from __future__ import annotations
import os
import json
from dataclasses import dataclass
from difflib import SequenceMatcher, unified_diff
from typing import List, Tuple, Dict, Any, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QAction
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QSplitter, QTextEdit, QVBoxLayout, QWidget,
    QPlainTextEdit, QCheckBox, QScrollArea, QSizePolicy, QInputDialog
)

# Try to import openai; if unavailable we fall back to stub behavior
try:
    import openai
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False


# --------------------------- LLM Client ----------------------------------
def on_suggestion_ready(result: dict):
    modified = result.get("modified_code", "")
    explanation = result.get("explanation", "")
    original = window.editor.toPlainText()

    if not modified.strip():
        QMessageBox.warning(window, "Empty AI Response", "The AI returned no code.")
        return

    if modified.strip() == original.strip():
        window.statusBar().showMessage("No changes from AI", 3000)
        return

    try:
        set_editor_full_text_generic(window.editor, modified)
        window.statusBar().showMessage("AI applied full edit", 3000)
    except Exception as e:
        QMessageBox.critical(window, "AI Apply Error", str(e))


# --------------------------- Worker & Manager -----------------------------
class _LLMWorker(QThread):
    finished_with_result = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, llm_client: LLMClient, mode: str, filename: str, full_code: str, payload: str):
        """
        mode: either 'edit' or 'qa'
        payload: instruction if mode == 'edit', or question if mode == 'qa'
        """
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
                raise RuntimeError("LLM did not return a dict.")
            self.finished_with_result.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class AIManager(QWidget):
    """
    Manages LLM worker threads and exposes simple signals:
      - suggestion_ready(dict)  # result from request_code_edit
      - suggestion_failed(str)
      - qa_ready(dict)  # result from answer_question
    """
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


# --------------------------- Diff/Hunk Utilities -----------------------------
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

# --- QScintilla-aware helpers (replace older apply_selected_hunks/get_editor_full_text) ---

def get_editor_full_text_generic(editor) -> str:
    """
    Return the full text of the editor whether it's QsciScintilla or QTextEdit/QPlainTextEdit.
    QsciScintilla provides .text(); QTextEdit uses toPlainText().
    """
    # QScintilla CodeEditor uses .text()
    if hasattr(editor, "text") and callable(getattr(editor, "text")):
        try:
            return editor.text()
        except Exception:
            pass
    # QTextEdit / QPlainTextEdit fallback
    if hasattr(editor, "toPlainText") and callable(getattr(editor, "toPlainText")):
        return editor.toPlainText()
    # As a last resort, try __str__
    return str(editor)

def set_editor_full_text_generic(editor, new_text: str):
    """
    Set the entire editor text. Use QsciScintilla.setText if available; otherwise toPlainText / setPlainText.
    """
    if hasattr(editor, "setText") and callable(getattr(editor, "setText")):
        try:
            editor.setText(new_text)
            return
        except Exception:
            pass
    if hasattr(editor, "setPlainText") and callable(getattr(editor, "setPlainText")):
        editor.setPlainText(new_text)
        return
    # fallback: try replacing via selection or raise
    raise RuntimeError("Unable to set editor text: unsupported editor widget")

def _char_index_to_line_col(text: str, char_idx: int) -> Tuple[int, int]:
    """
    Convert a character index into (line, col) with 0-based line and col suitable for QsciScintilla.setSelection.
    """
    if char_idx <= 0:
        return 0, 0
    # count lines up to char_idx
    # splitlines keeps no trailing newline; we'll iterate
    upto = text[:char_idx]
    line = upto.count("\n")
    if line == 0:
        col = len(upto)
    else:
        # find position of last newline
        last_nl = upto.rfind("\n")
        col = len(upto) - last_nl - 1
    return line, col

def apply_selected_hunks(editor, hunks: List[DiffHunk]):
    """
    Universal apply_selected_hunks that supports QsciScintilla (Qsci) and QTextEdit/QPlainTextEdit.
    - For QsciScintilla: convert char indices -> (line, col), call setSelection(start_line,start_col,end_line,end_col) and replaceSelectedText()
    - For QTextEdit: use QTextCursor on document()
    If many hunks exist we apply them in reverse order to keep indices stable.
    """
    # If no hunks: nothing to do
    if not hunks:
        return

    # Detect QScintilla by presence of setSelection/replaceSelectedText methods
    is_qsci = hasattr(editor, "setSelection") and hasattr(editor, "replaceSelectedText")

    # Get current full text as a fallback / for conversions
    try:
        full_text = get_editor_full_text_generic(editor)
    except Exception:
        full_text = ""

    # Apply hunks in reverse order by old_start
    for h in sorted(hunks, key=lambda x: x.old_start, reverse=True):
        if is_qsci:
            # convert char indices to (line, col)
            start_line, start_col = _char_index_to_line_col(full_text, h.old_start)
            end_line, end_col = _char_index_to_line_col(full_text, h.old_end)
            # select and replace
            try:
                editor.setSelection(start_line, start_col, end_line, end_col)
                # QScintilla.replaceSelectedText expects the replacement string
                editor.replaceSelectedText(h.new_text)
            except Exception as e:
                # fallback to whole-file replace if selection API fails
                new_full = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
                set_editor_full_text_generic(editor, new_full)
                full_text = new_full
                continue
            # update our cached full_text since content changed
            full_text = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
        else:
            # Try QTextCursor replacement (works for QTextEdit/QPlainTextEdit)
            try:
                doc = editor.document()
                cursor = QTextCursor(doc)
                cursor.setPosition(h.old_start)
                cursor.setPosition(h.old_end, QTextCursor.MoveMode.KeepAnchor)
                cursor.beginEditBlock()
                cursor.insertText(h.new_text)
                cursor.endEditBlock()
                # update cached full_text
                full_text = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
            except Exception:
                # If anything fails, fallback to whole-file replacement
                new_full = full_text[:h.old_start] + h.new_text + full_text[h.old_end:]
                set_editor_full_text_generic(editor, new_full)
                full_text = new_full


# --------------------------- GUI: Hunk Preview & QA Dialogs -----------------
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
        ans_view = QTextEdit()
        ans_view.setReadOnly(True)
        ans_view.setPlainText(answer)
        layout.addWidget(ans_view)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# --------------------------- Integration Helper -----------------------------
def install_ai_actions(window):
    """
    Install AI Suggest Edit and AI QA actions into MainWindow-like object.

    Requirements on window:
      - window.editor : QPlainTextEdit
      - window.current_file_path attribute (optional)
      - window.statusBar() available
    """
    llm_client = LLMClient(config={"provider": "openai" if _HAS_OPENAI and os.getenv("OPENAI_API_KEY") else "stub"})
    ai_manager = AIManager(llm_client)

# def on_suggestion_ready(result: dict):
#     modified = result.get("modified_code", "")
#     explanation = result.get("explanation", "")
#     original = window.editor.toPlainText()

#     if not modified.strip():
#         QMessageBox.warning(window, "Empty AI response", "No code returned from the AI.")
#         return

#     if modified.strip() == original.strip():
#         window.statusBar().showMessage("No changes from AI", 3000)
#         return

#     # Directly replace editor text
#     try:
#         set_editor_full_text_generic(window.editor, modified)
#         window.statusBar().showMessage("AI applied full edit", 3000)
#     except Exception as e:
#         QMessageBox.critical(window, "AI Apply Error", str(e))


#     def on_suggestion_failed(msg: str):
#         QMessageBox.critical(window, "AI Suggestion failed", f"LLM error: {msg}")

#     def on_qa_ready(result: dict):
#         answer = result.get("answer", "")
#         question = getattr(window, "_last_ai_question", "<question>")
#         dlg = QAResponseDialog(window, question, answer)
#         dlg.exec()

#     def on_qa_failed(msg: str):
#         QMessageBox.critical(window, "AI QA failed", f"LLM error: {msg}")

#     ai_manager.suggestion_ready.connect(on_suggestion_ready)
#     ai_manager.suggestion_failed.connect(on_suggestion_failed)
#     ai_manager.qa_ready.connect(on_qa_ready)
#     ai_manager.qa_failed.connect(on_qa_failed)

#     # AI Suggest Edit action
#     ai_action = QAction("AI Suggest Edit", window)
#     ai_action.setShortcut("Ctrl+Alt+S")

#     def trigger_ai_suggest():
#         filename = getattr(window, "current_file_path", "<untitled>")
#         full_code = window.editor.toPlainText()
#         # Ask the user for instruction text (quick input) -- default prompt provided
#         instr, ok = QInputDialog.getText(window, "AI Instruction", "Instruction for AI (edit request):", text="Improve code quality, fix bugs, and follow PEP8 where applicable.")
#         if not ok:
#             return
#         instruction = instr
#         window.statusBar().showMessage("Requesting AI suggestion...")
#         ai_manager.request_suggestion(filename=filename, full_code=full_code, instruction=instruction)

#     ai_action.triggered.connect(trigger_ai_suggest)
#     window.menuBar().addAction(ai_action)
#     window.addAction(ai_action)

#     # AI QA action
#     qa_action = QAction("AI Ask about File", window)
#     qa_action.setShortcut("Ctrl+Alt+Q")

#     def trigger_ai_qa():
#         filename = getattr(window, "current_file_path", "<untitled>")
#         full_code = window.editor.toPlainText()
#         question, ok = QInputDialog.getText(window, "Ask AI about file", "Question about the current open file:")
#         if not ok or not question.strip():
#             return
#         # store question for the response dialog
#         window._last_ai_question = question
#         window.statusBar().showMessage("Asking AI...")
#         ai_manager.request_qa(filename=filename, full_code=full_code, question=question)

#     qa_action.triggered.connect(trigger_ai_qa)
#     window.menuBar().addAction(qa_action)
#     window.addAction(qa_action)

#     # Persist to window to avoid GC and allow later customization
#     window._ai_manager = ai_manager
#     window._llm_client = llm_client

#     return ai_manager