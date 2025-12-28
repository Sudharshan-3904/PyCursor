import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, 
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QProgressBar,
    QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from core.ui.theme import COLORS
from core.utilities.utils import load_icon

class SearchWorker(QThread):
    """Background thread for searching files"""
    match_found = pyqtSignal(str, int, str) # file_path, line_num, line_content
    finished = pyqtSignal()
    progress = pyqtSignal(int) # Processed files count

    def __init__(self, root_path, query, use_regex=False, match_case=False, whole_word=False, include_pattern="", exclude_pattern=""):
        super().__init__()
        self.root_path = root_path
        self.query = query
        self.use_regex = use_regex
        self.match_case = match_case
        self.whole_word = whole_word
        self.include_pattern = include_pattern
        self.exclude_pattern = exclude_pattern
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.query:
            self.finished.emit()
            return

        # Prepare regex pattern if needed
        try:
            ignore_case_flag = 0 if self.match_case else re.IGNORECASE
            
            if self.use_regex:
                pattern = re.compile(self.query, ignore_case_flag)
            else:
                # Escape if not using regex, but standard find is faster if we don't need regex
                # We'll use regex for whole word/case support flexibility though
                escaped_query = re.escape(self.query)
                if self.whole_word:
                    escaped_query = f"\\b{escaped_query}\\b"
                pattern = re.compile(escaped_query, ignore_case_flag)
                
        except re.error:
            # Invalid regex
            self.finished.emit()
            return

        # Walk directory
        count = 0
        
        # Simple exclude list for performance (folders)
        common_excludes = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode'}

        for root, dirs, files in os.walk(self.root_path):
            if not self.is_running:
                break
                
            # Filter dirs in-place
            dirs[:] = [d for d in dirs if d not in common_excludes]
            
            for file in files:
                if not self.is_running:
                    break
                    
                file_path = os.path.join(root, file)
                count += 1
                if count % 100 == 0:
                    self.progress.emit(count)

                # TODO: Implement Include/Exclude patterns check here (fnmatch)
                
                # Reading file
                try:
                    # Skip binary files check could be added here
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if pattern.search(line):
                                self.match_found.emit(file_path, i + 1, line.strip())
                except Exception:
                    continue
        
        self.finished.emit()


class SearchPanel(QWidget):
    """
    Search in Files Panel
    """
    file_selected = pyqtSignal(str, int)  # path, line_number

    def __init__(self, root_path=None):
        super().__init__()
        self.root_path = root_path
        self.worker = None
        self.setup_ui()

    def set_project_path(self, path):
        self.root_path = path

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QLabel("SEARCH")
        header.setStyleSheet(f"font-weight: bold; color: {COLORS['text_secondary']}; padding: 10px 10px 5px 10px;")
        layout.addWidget(header)

        # Search Input Area
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(10, 0, 10, 10)
        input_layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.returnPressed.connect(self.start_search)
        input_layout.addWidget(self.search_input)

        # Toggle Options
        options_layout = QHBoxLayout()
        
        self.case_btn = self.create_toggle_button("Aa", "Match Case")
        self.word_btn = self.create_toggle_button("ab", "Match Whole Word") # rudimentary icon approach
        self.regex_btn = self.create_toggle_button(".*", "Use Regular Expression")
        
        options_layout.addWidget(self.case_btn)
        options_layout.addWidget(self.word_btn)
        options_layout.addWidget(self.regex_btn)
        options_layout.addStretch()
        input_layout.addLayout(options_layout)
        
        # Include/Exclude (collapsible ideally, but expanded for now)
        self.include_input = QLineEdit()
        self.include_input.setPlaceholderText("files to include (e.g. *.py)")
        input_layout.addWidget(self.include_input)
        
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("files to exclude")
        input_layout.addWidget(self.exclude_input)

        layout.addWidget(input_container)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"QProgressBar {{ border: none; background: {COLORS['bg_secondary']}; }} QProgressBar::chunk {{ background: {COLORS['accent_blue']}; }}")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderHidden(True)
        self.results_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: transparent;
                border: none;
            }}
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {COLORS['list_hover']};
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['list_selected']};
            }}
        """)
        self.results_tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.results_tree)
        
        # Clear button logic implicit in new search
        
    def create_toggle_button(self, text, tooltip):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setFixedSize(25, 25)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['bg_selection']};
                color: {COLORS['text_highlight']};
                border: 1px solid {COLORS['accent_blue']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_elevated']};
            }}
        """)
        return btn

    def start_search(self):
        query = self.search_input.text()
        if not query:
            return
            
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            
        self.results_tree.clear()
        self.file_items = {} # Map path -> QTreeWidgetItem
        self.match_count = 0
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate mode

        self.worker = SearchWorker(
            self.root_path,
            query,
            self.regex_btn.isChecked(),
            self.case_btn.isChecked(),
            self.word_btn.isChecked(),
            self.include_input.text(),
            self.exclude_input.text()
        )
        
        self.worker.match_found.connect(self.add_match)
        self.worker.finished.connect(self.search_finished)
        self.worker.start()

    def add_match(self, file_path, line_num, line_content):
        # Group by file
        if file_path not in self.file_items:
            item = QTreeWidgetItem(self.results_tree)
            rel_path = os.path.relpath(file_path, self.root_path)
            item.setText(0, f"{os.path.basename(file_path)} {os.path.dirname(rel_path)}")
            item.setToolTip(0, file_path)
            item.setData(0, Qt.ItemDataRole.UserRole, file_path)
            # Make file items bold/different color could be nice
            # item.setForeground(0, QBrush(QColor(...)))
            item.setExpanded(True)
            self.file_items[file_path] = item
            
        parent = self.file_items[file_path]
        child = QTreeWidgetItem(parent)
        # Truncate line content if too long
        display_content = (line_content[:50] + '...') if len(line_content) > 50 else line_content
        child.setText(0, f"{line_num}: {display_content}")
        # Store line number in UserRole
        child.setData(0, Qt.ItemDataRole.UserRole, (file_path, line_num))
        
        self.match_count += 1

    def search_finished(self):
        self.progress_bar.setVisible(False)
        # Maybe show status "X matches found"
        pass

    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            # It's a match line: (path, line)
            self.file_selected.emit(data[0], data[1])
        elif isinstance(data, str):
            # It's a file header
            # toggle expansion? Default behavior handles this.
            pass
