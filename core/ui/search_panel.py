"""
Search and Discovery Panel for PyCursor IDE.
Provides project-wide string searching with support for literal matches, 
regular expressions, case sensitivity, and whole-word filtering.
"""

import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, 
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.ui.theme import COLORS

class SearchWorker(QThread):
    """
    Background worker for executing intensive file system search operations.
    Communicates results back to the UI thread via signals to maintain responsiveness.
    """
    match_found = pyqtSignal(str, int, str) # Signals: (file_path, line_number, preview_text)
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, root_path: str, query: str, regex: bool, case: bool, word: bool):
        super().__init__()
        self.root_path = root_path
        self.query = query
        self.use_regex = regex
        self.match_case = case
        self.whole_word = word
        self.active = True

    def stop(self):
        """Signals the worker thread to abort the current search loop."""
        self.active = False

    def run(self):
        """
        Primary search execution loop. Traverses the directory tree and scans file contents.
        """
        if not self.query:
            self.finished.emit()
            return

        try:
            # Prepare search pattern based on user configuration
            flags = 0 if self.match_case else re.IGNORECASE
            if self.use_regex:
                pattern = re.compile(self.query, flags)
            else:
                raw_q = re.escape(self.query)
                if self.whole_word: raw_q = f"\\b{raw_q}\\b"
                pattern = re.compile(raw_q, flags)
        except re.error:
            self.finished.emit()
            return

        # Optimization: Folders to bypass during traversal
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}

        for root, dirs, files in os.walk(self.root_path):
            if not self.active: break
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for f in files:
                if not self.active: break
                path = os.path.join(root, f)
                
                try:
                    # Scan file line-by-line using streaming to conserve memory
                    with open(path, 'r', encoding='utf-8', errors='ignore') as handle:
                        for idx, line in enumerate(handle):
                            if pattern.search(line):
                                self.match_found.emit(path, idx + 1, line.strip())
                except Exception:
                    continue
        
        self.finished.emit()

class SearchPanel(QWidget):
    """
    UI component for initiating global searches and displaying hierarchical results.
    """
    # Signal emitted when a user selects a specific match in the result tree
    match_activated = pyqtSignal(str, int) 
    # Signal emitted when a user selects a file in the result tree
    file_selected = pyqtSignal(str) 

    def __init__(self, root_path=None):
        super().__init__()
        self.root_path = root_path
        self.worker = None
        self._init_ui()

    def set_project_path(self, path: str):
        """Updates the search scope to the new project root."""
        self.root_path = path

    def _init_ui(self):
        """Constructs the sidebar search interface."""
        view = QVBoxLayout(self)
        view.setContentsMargins(0, 0, 0, 0)
        view.setSpacing(0)

        header = QLabel("SEARCH")
        header.setStyleSheet(f"font-weight: bold; color: {COLORS['text_secondary']}; padding: 10px;")
        view.addWidget(header)

        # Search Controls Group
        ctrls = QWidget()
        ctrls_layout = QVBoxLayout(ctrls)
        self.query_field = QLineEdit()
        self.query_field.setPlaceholderText("Search patterns...")
        self.query_field.returnPressed.connect(self.execute_search)
        ctrls_layout.addWidget(self.query_field)

        # Options Strip (Regex, Case, Word)
        options = QHBoxLayout()
        self.case_toggle = self._create_option_btn("Aa", "Match Case")
        self.word_toggle = self._create_option_btn("W", "Whole Word")
        self.regex_toggle = self._create_option_btn(".*", "Regex")
        options.addWidget(self.case_toggle)
        options.addWidget(self.word_toggle)
        options.addWidget(self.regex_toggle)
        options.addStretch()
        ctrls_layout.addLayout(options)
        view.addWidget(ctrls)

        # Real-time Progress Indicator
        self.spinner = QProgressBar()
        self.spinner.setFixedHeight(2)
        self.spinner.setTextVisible(False)
        self.spinner.setVisible(False)
        view.addWidget(self.spinner)

        # Result Listing
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        view.addWidget(self.tree)

    def _create_option_btn(self, label, tip):
        """Helper to create consistent toggle buttons for search modifiers."""
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setToolTip(tip)
        btn.setFixedSize(26, 26)
        btn.setStyleSheet(f"QPushButton {{ background: transparent; border-radius: 4px; }} "
                          f"QPushButton:checked {{ background: {COLORS['bg_selection']}; border: 1px solid {COLORS['accent_blue']}; }}")
        return btn

    def execute_search(self):
        """
        Initializes and starts the background search worker with current UI settings.
        """
        query = self.query_field.text()
        if not query: return
            
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            
        self.tree.clear()
        self.file_nodes = {} # Cache for file-level parent items
        self.spinner.setVisible(True)
        self.spinner.setRange(0, 0)

        self.worker = SearchWorker(
            self.root_path, query, 
            self.regex_toggle.isChecked(),
            self.case_toggle.isChecked(),
            self.word_toggle.isChecked()
        )
        self.worker.match_found.connect(self._add_result_entry)
        self.worker.finished.connect(lambda: self.spinner.setVisible(False))
        self.worker.start()

    def _add_result_entry(self, path, line, content):
        """
        Populates the result tree with a match, grouping by file.
        """
        if path not in self.file_nodes:
            rel = os.path.relpath(path, self.root_path)
            node = QTreeWidgetItem(self.tree, [os.path.basename(path)])
            node.setToolTip(0, rel)
            node.setData(0, Qt.ItemDataRole.UserRole, path)  # Store full path for file nodes
            node.setExpanded(True)
            self.file_nodes[path] = node
            
        parent = self.file_nodes[path]
        child = QTreeWidgetItem(parent, [f"{line}: {content[:60]}"])
        child.setData(0, Qt.ItemDataRole.UserRole, (path, line))

    def _on_item_clicked(self, item, col):
        """Handles navigation to the specific file/line when a result is clicked."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            # Match item clicked - emit match_activated with file path and line number
            self.match_activated.emit(data[0], data[1])
        elif isinstance(data, str):
            # File node clicked - emit file_selected with file path
            self.file_selected.emit(data)
