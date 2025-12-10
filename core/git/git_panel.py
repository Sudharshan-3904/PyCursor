"""
Git Panel UI for PyCursor IDE

Provides a visual interface for Git operations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QTextEdit, QSplitter,
    QComboBox, QMessageBox, QInputDialog, QMenu, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from core.ui.theme import COLORS
from core.git.git_handler import GitHandler, GitFileStatus
import os


class GitPanel(QWidget):
    """Git panel widget for the sidebar"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, repo_path: str = None):
        super().__init__()
        self.git_handler = GitHandler(repo_path)
        self.repo_path = repo_path
        self.init_ui()
        
        # self.update_view() # Deferred to startup thread
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # 1. No Repo View
        self.no_repo_widget = self.create_no_repo_widget()
        self.stack.addWidget(self.no_repo_widget)
        
        # 2. Repo View
        self.repo_widget = self.create_repo_widget()
        self.stack.addWidget(self.repo_widget)

    def create_no_repo_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        label = QLabel("No Git Repository")
        label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px; font-weight: bold;")
        layout.addWidget(label)
        
        init_btn = QPushButton("Initialize Repository")
        init_btn.clicked.connect(self.init_repo)
        init_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #4a9eff;
            }}
        """)
        layout.addWidget(init_btn)
        
        clone_btn = QPushButton("Clone Repository")
        clone_btn.clicked.connect(self.clone_repo)
        clone_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_elevated']};
            }}
        """)
        layout.addWidget(clone_btn)
        
        return widget

    def create_repo_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        widget.setLayout(layout)
        
        # Branch and actions header
        header_layout = QHBoxLayout()
        
        self.branch_combo = QComboBox()
        self.branch_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
            }}
        """)
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)
        header_layout.addWidget(self.branch_combo)
        
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 3px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.pull_btn = QPushButton("Pull")
        self.pull_btn.clicked.connect(self.pull)
        actions_layout.addWidget(self.pull_btn)
        
        self.push_btn = QPushButton("Push")
        self.push_btn.clicked.connect(self.push)
        actions_layout.addWidget(self.push_btn)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.clicked.connect(self.fetch)
        actions_layout.addWidget(self.fetch_btn)
        
        for btn in [self.pull_btn, self.push_btn, self.fetch_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['button_bg']};
                    color: {COLORS['text_primary']};
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['button_hover']};
                }}
            """)
        
        layout.addLayout(actions_layout)
        
        # Splitter for changes and commit message
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Changes tree
        changes_widget = QWidget()
        changes_layout = QVBoxLayout()
        changes_layout.setContentsMargins(0, 0, 0, 0)
        changes_widget.setLayout(changes_layout)
        
        changes_label = QLabel("Changes")
        changes_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: bold;")
        changes_layout.addWidget(changes_label)
        
        self.changes_tree = QTreeWidget()
        self.changes_tree.setHeaderHidden(True)
        self.changes_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.changes_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.changes_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.changes_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
            }}
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {COLORS['sidebar_hover']};
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['sidebar_selected']};
            }}
        """)
        changes_layout.addWidget(self.changes_tree)
        
        stage_all_layout = QHBoxLayout()
        self.stage_all_btn = QPushButton("Stage All")
        self.stage_all_btn.clicked.connect(self.stage_all)
        stage_all_layout.addWidget(self.stage_all_btn)
        
        self.unstage_all_btn = QPushButton("Unstage All")
        self.unstage_all_btn.clicked.connect(self.unstage_all)
        stage_all_layout.addWidget(self.unstage_all_btn)
        
        for btn in [self.stage_all_btn, self.unstage_all_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_elevated']};
                }}
            """)
        
        changes_layout.addLayout(stage_all_layout)
        
        splitter.addWidget(changes_widget)
        
        # Commit section
        commit_widget = QWidget()
        commit_layout = QVBoxLayout()
        commit_layout.setContentsMargins(0, 0, 0, 0)
        commit_widget.setLayout(commit_layout)
        
        commit_label = QLabel("Commit Message")
        commit_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: bold;")
        commit_layout.addWidget(commit_label)
        
        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("Enter commit message...")
        self.commit_message.setMaximumHeight(80)
        self.commit_message.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
            }}
        """)
        commit_layout.addWidget(self.commit_message)
        
        self.commit_btn = QPushButton("Commit")
        self.commit_btn.clicked.connect(self.commit)
        self.commit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_green']};
                color: {COLORS['bg_primary']};
                border: none;
                border-radius: 3px;
                padding: 6px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5ec9a0;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_disabled']};
            }}
        """)
        commit_layout.addWidget(self.commit_btn)
        
        splitter.addWidget(commit_widget)
        splitter.setSizes([300, 150])
        
        layout.addWidget(splitter)
        return widget
    
    def update_view(self):
        """Update the view based on repo status"""
        if self.repo_path and self.git_handler.is_repository(self.repo_path):
            self.stack.setCurrentWidget(self.repo_widget)
            self.refresh()
        else:
            self.stack.setCurrentWidget(self.no_repo_widget)

    def init_repo(self):
        """Initialize a new repository"""
        if not self.repo_path:
            return
            
        if self.git_handler.init_repository(self.repo_path):
            self.update_view()
            QMessageBox.information(self, "Success", "Repository initialized successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to initialize repository")

    def clone_repo(self):
        """Clone a repository"""
        if not self.repo_path:
            return
            
        url, ok = QInputDialog.getText(self, "Clone Repository", "Enter Repository URL:")
        if ok and url:
            # Show progress dialog or loading state here if possible
            if self.git_handler.clone_repository(url, self.repo_path):
                self.update_view()
                QMessageBox.information(self, "Success", "Repository cloned successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to clone repository")

    def set_repository(self, repo_path: str):
        """Set the repository path"""
        self.repo_path = repo_path
        if self.git_handler.open_repository(repo_path):
            self.refresh()
        self.update_view()
    
    def refresh(self, status=None, branches=None, current_branch=None):
        """Refresh the Git status"""
        if not self.git_handler.repo:
            return
        
        # Update branches
        self.branch_combo.blockSignals(True)
        self.branch_combo.clear()
        
        if current_branch is None:
            current_branch = self.git_handler.get_current_branch()
        
        if branches is None:
            branches = self.git_handler.get_branches()
        
        self.branch_combo.addItems(branches)
        if current_branch:
            self.branch_combo.setCurrentText(current_branch)
        self.branch_combo.blockSignals(False)
        
        # Update changes tree
        self.changes_tree.clear()
        
        staged_root = QTreeWidgetItem(self.changes_tree, ["Staged Changes"])
        staged_root.setExpanded(True)
        
        unstaged_root = QTreeWidgetItem(self.changes_tree, ["Changes"])
        unstaged_root.setExpanded(True)
        
        if status is None:
            status = self.git_handler.get_status()
        
        for file_status in status:
            icon_text = self.get_status_icon(file_status.status)
            item_text = f"{icon_text} {file_status.path}"
            
            item = QTreeWidgetItem([item_text])
            item.setData(0, Qt.ItemDataRole.UserRole, file_status)
            
            if file_status.staged:
                staged_root.addChild(item)
            else:
                unstaged_root.addChild(item)
        
        # Update button states
        has_staged = staged_root.childCount() > 0
        self.commit_btn.setEnabled(has_staged)
    
    def get_status_icon(self, status: str) -> str:
        """Get icon for file status"""
        icons = {
            'modified': 'M',
            'added': 'A',
            'deleted': 'D',
            'untracked': 'U',
            'renamed': 'R'
        }
        return icons.get(status, '?')
    
    def on_branch_changed(self, branch_name: str):
        """Handle branch change"""
        if not branch_name or not self.git_handler.repo:
            return
        
        current = self.git_handler.get_current_branch()
        if branch_name != current:
            reply = QMessageBox.question(
                self, "Checkout Branch",
                f"Switch to branch '{branch_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.git_handler.checkout_branch(branch_name):
                    self.refresh()
                    QMessageBox.information(self, "Success", f"Switched to branch '{branch_name}'")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to checkout branch '{branch_name}'")
                    self.branch_combo.setCurrentText(current)
    
    def show_context_menu(self, position):
        """Show context menu for file items"""
        item = self.changes_tree.itemAt(position)
        if not item or not item.parent():
            return
        
        file_status = item.data(0, Qt.ItemDataRole.UserRole)
        if not file_status:
            return
        
        menu = QMenu(self)
        
        if file_status.staged:
            unstage_action = QAction("Unstage", self)
            unstage_action.triggered.connect(lambda: self.unstage_file(file_status.path))
            menu.addAction(unstage_action)
        else:
            stage_action = QAction("Stage", self)
            stage_action.triggered.connect(lambda: self.stage_file(file_status.path))
            menu.addAction(stage_action)
            
            if file_status.status != 'untracked':
                discard_action = QAction("Discard Changes", self)
                discard_action.triggered.connect(lambda: self.discard_changes(file_status.path))
                menu.addAction(discard_action)
        
        menu.addSeparator()
        
        diff_action = QAction("View Diff", self)
        diff_action.triggered.connect(lambda: self.view_diff(file_status.path, file_status.staged))
        menu.addAction(diff_action)
        
        menu.exec(self.changes_tree.mapToGlobal(position))
    
    def on_file_double_clicked(self, item, column):
        """Handle file double click"""
        if not item.parent():
            return
        
        file_status = item.data(0, Qt.ItemDataRole.UserRole)
        if file_status:
            full_path = os.path.join(self.repo_path, file_status.path)
            self.file_selected.emit(full_path)
    
    def stage_file(self, file_path: str):
        """Stage a file"""
        if self.git_handler.stage_file(file_path):
            self.refresh()
    
    def unstage_file(self, file_path: str):
        """Unstage a file"""
        if self.git_handler.unstage_file(file_path):
            self.refresh()
    
    def stage_all(self):
        """Stage all changes"""
        if self.git_handler.stage_all():
            self.refresh()
    
    def unstage_all(self):
        """Unstage all changes"""
        # Reset all staged files
        if self.git_handler.repo:
            try:
                self.git_handler.repo.index.reset()
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to unstage all: {e}")
    
    def discard_changes(self, file_path: str):
        """Discard changes in a file"""
        reply = QMessageBox.question(
            self, "Discard Changes",
            f"Discard all changes in '{file_path}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.git_handler.discard_changes(file_path):
                self.refresh()
                QMessageBox.information(self, "Success", "Changes discarded")
    
    def commit(self):
        """Commit staged changes"""
        message = self.commit_message.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "No Message", "Please enter a commit message")
            return
        
        if self.git_handler.commit(message):
            self.commit_message.clear()
            self.refresh()
            QMessageBox.information(self, "Success", "Changes committed successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to commit changes")
    
    def pull(self):
        """Pull from remote"""
        success, message = self.git_handler.pull()
        if success:
            self.refresh()
            QMessageBox.information(self, "Success", "Pull completed successfully")
        else:
            QMessageBox.warning(self, "Error", f"Pull failed: {message}")
    
    def push(self):
        """Push to remote"""
        success, message = self.git_handler.push()
        if success:
            QMessageBox.information(self, "Success", "Push completed successfully")
        else:
            QMessageBox.warning(self, "Error", f"Push failed: {message}")
    
    def fetch(self):
        """Fetch from remote"""
        if self.git_handler.fetch():
            self.refresh()
            QMessageBox.information(self, "Success", "Fetch completed successfully")
        else:
            QMessageBox.warning(self, "Error", "Fetch failed")
    
    def view_diff(self, file_path: str, staged: bool):
        """View diff for a file"""
        diff = self.git_handler.get_file_diff(file_path, staged)
        if diff:
            from core.ui.diff_viewer import DiffViewer
            viewer = DiffViewer(file_path, diff, self)
            viewer.exec()
