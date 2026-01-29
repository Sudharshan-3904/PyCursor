from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QTextEdit, QSplitter,
    QComboBox, QMessageBox, QInputDialog, QMenu, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from core.ui.theme import COLORS
from core.git.git_handler import GitHandler, GitFileStatus
from core.utilities.worker import WorkerThread
import os

class GitPanel(QWidget) :
    """
    Git Management Panel located in the sidebar.
    Provides visualization of repository status, staging/committing workflows,
    and remote synchronization features (Push/Pull/Fetch).
    """
    file_selected = pyqtSignal(str)
    
    def __init__(self, repo_path: str = None):
        """
        Initializes the panel and binds to a Git repository if provided.
        """
        super().__init__()
        self.git_handler = GitHandler(repo_path)
        self.repo_path = repo_path
        self._init_ui()

    def _init_ui(self):
        """
        Constructs the state-driven UI with multiple views (No Repo vs Active Repo).
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # View: Displayed when working in a non-git directory
        self.no_repo_widget = self._create_no_repo_view()
        self.stack.addWidget(self.no_repo_widget)
        
        # View: Primary interface for active Git repositories
        self.repo_widget = self._create_active_repo_view()
        self.stack.addWidget(self.repo_widget)

    def _create_no_repo_view(self) :
        """
        UI for initiating Git tracking in the current project.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        label = QLabel("No Git Repository")
        layout.addWidget(label)
        
        init_btn = QPushButton("Initialize Repository")
        init_btn.clicked.connect(self.init_repo)
        layout.addWidget(init_btn)
        
        clone_btn = QPushButton("Clone Repository")
        clone_btn.clicked.connect(self.clone_repo)
        layout.addWidget(clone_btn)
        
        return widget

    def _create_active_repo_view(self) :
        """
        Main interface for SCM operations (branching, staging, committing).
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header: Branch control and refresh
        header = QHBoxLayout()
        self.branch_combo = QComboBox()
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)
        header.addWidget(self.branch_combo)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self.refresh_btn)
        layout.addLayout(header)
        
        # Toolbelt: Remote Operations
        remote_ops = QHBoxLayout()
        self.pull_btn = QPushButton("Pull")
        self.pull_btn.clicked.connect(self.pull)
        remote_ops.addWidget(self.pull_btn)
        
        self.push_btn = QPushButton("Push")
        self.push_btn.clicked.connect(self.push)
        remote_ops.addWidget(self.push_btn)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.clicked.connect(self.fetch)
        remote_ops.addWidget(self.fetch_btn)
        layout.addLayout(remote_ops)
        
        # Body: Changes Tree and Commit Interface
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Changes Section
        changes_panel = QWidget()
        changes_layout = QVBoxLayout(changes_panel)
        self.changes_tree = QTreeWidget()
        self.changes_tree.setHeaderHidden(True)
        self.changes_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.changes_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.changes_tree.itemDoubleClicked.connect(self._on_file_activated)
        changes_layout.addWidget(QLabel("Changes"))
        changes_layout.addWidget(self.changes_tree)
        
        bulk_stage_ops = QHBoxLayout()
        self.stage_all_btn = QPushButton("Stage All")
        self.stage_all_btn.clicked.connect(self.stage_all)
        bulk_stage_ops.addWidget(self.stage_all_btn)
        
        self.unstage_all_btn = QPushButton("Unstage All")
        self.unstage_all_btn.clicked.connect(self.unstage_all)
        bulk_stage_ops.addWidget(self.unstage_all_btn)
        changes_layout.addLayout(bulk_stage_ops)
        splitter.addWidget(changes_panel)
        
        # Commit Section
        commit_panel = QWidget()
        commit_layout = QVBoxLayout(commit_panel)
        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("Commit message...")
        self.commit_message.setMaximumHeight(80)
        self.commit_btn = QPushButton("Commit")
        self.commit_btn.clicked.connect(self.commit)
        commit_layout.addWidget(QLabel("Commit Message"))
        commit_layout.addWidget(self.commit_message)
        commit_layout.addWidget(self.commit_btn)
        splitter.addWidget(commit_panel)
        
        layout.addWidget(splitter)
        return widget
    
    def refresh(self, status=None, branches=None, current_branch=None):
        """
        Asynchronously refreshes the Git status and update UI components.
        Accepts pre-computed data from external threads to avoid redundant work.
        """
        if status is not None:
            self._update_repository_state(status, branches, current_branch)
            return

        # Start background discovery
        self.refresh_btn.setEnabled(False)
        self.worker = WorkerThread(lambda: (
            self.git_handler.get_status(),
            self.git_handler.get_branches(),
            self.git_handler.get_current_branch()
        ))
        self.worker.result_ready.connect(lambda res: self._update_repository_state(*res))
        self.worker.finished.connect(lambda: self.refresh_btn.setEnabled(True))
        self.worker.start()

    def _update_repository_state(self, status, branches, current):
        """
        Updates the UI to reflect the current state of the repository.
        """
        self.branch_combo.blockSignals(True)
        self.branch_combo.clear()
        self.branch_combo.addItems(branches)
        if current: self.branch_combo.setCurrentText(current)
        self.branch_combo.blockSignals(False)
        
        self.changes_tree.clear()
        staged_grp = QTreeWidgetItem(self.changes_tree, ["Staged Changes"])
        changes_grp = QTreeWidgetItem(self.changes_tree, ["Changes"])
        staged_grp.setExpanded(True)
        changes_grp.setExpanded(True)
        
        for fs in status:
            item = QTreeWidgetItem([f"[{fs.status[0].upper()}] {fs.path}"])
            item.setData(0, Qt.ItemDataRole.UserRole, fs)
            (staged_grp if fs.staged else changes_grp).addChild(item)
        
        self.commit_btn.setEnabled(staged_grp.childCount() > 0)

    def on_branch_changed(self, branch):
        """
        Handles branch switching with user confirmation.
        """
        if not branch: return
        confirm = QMessageBox.question(self, "Checkout", f"Switch to branch '{branch}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.git_handler.checkout_branch(branch)
            self.refresh()
        else:
            self.refresh()

    def show_context_menu(self, pos):
        """
        Shows contextual actions for individual file entries (Stage, Unstage, Discard).
        """
        item = self.changes_tree.itemAt(pos)
        if not item or not item.parent(): return
        
        fs = item.data(0, Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        
        if fs.staged:
            menu.addAction("Unstage File", lambda: self.unstage_file(fs.path))
        else:
            menu.addAction("Stage File", lambda: self.stage_file(fs.path))
            if fs.status != 'untracked':
                menu.addAction("Discard Changes", lambda: self.discard_changes(fs.path))
        
        menu.addSeparator()
        menu.addAction("View Diff", lambda: self.view_diff(fs.path, fs.staged))
        menu.exec(self.changes_tree.viewport().mapToGlobal(pos))

    def commit(self):
        """
        Finalizes the staged changes into a new commit.
        """
        msg = self.commit_message.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Validation", "Commit message is required.")
            return
        
        if self.git_handler.commit(msg):
            self.commit_message.clear()
            self.refresh()

    def init_repo(self):
        if self.git_handler.init_repository(self.repo_path):
            self.stack.setCurrentWidget(self.repo_widget)
            self.refresh()

    def clone_repo(self):
        url, ok = QInputDialog.getText(self, "Clone", "Repository URL:")
        if ok and url:
            if self.git_handler.clone_repository(url, self.repo_path):
                self.stack.setCurrentWidget(self.repo_widget)
                self.refresh()

    def pull(self): self._run_op(self.git_handler.pull)
    def push(self): self._run_op(self.git_handler.push)
    def fetch(self): self._run_op(self.git_handler.fetch)

    def stage_file(self, path): self.git_handler.stage_file(path); self.refresh()
    def unstage_file(self, path): self.git_handler.unstage_file(path); self.refresh()
    def stage_all(self): self.git_handler.stage_all(); self.refresh()
    def unstage_all(self): self.git_handler.repo.index.reset(); self.refresh()
    
    def discard_changes(self, path):
        if QMessageBox.warning(self, "Discard", f"Lost all changes in {path}?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.git_handler.discard_changes(path); self.refresh()

    def _on_file_activated(self, item, col):
        fs = item.data(0, Qt.ItemDataRole.UserRole)
        if fs: self.file_selected.emit(os.path.join(self.repo_path, fs.path))

    def _run_op(self, func):
        self.worker = WorkerThread(func)
        self.worker.result_ready.connect(self.refresh)
        self.worker.start()

    def view_diff(self, path, staged):
        diff = self.git_handler.get_file_diff(path, staged)
        if diff:
            from core.ui.diff_viewer import DiffViewer
            DiffViewer(path, diff, self).exec()

    def show_blame(self, path):
        rel = os.path.relpath(path, self.repo_path)
        data = self.git_handler.get_file_blame(rel)
        if data:
            from core.ui.git_dialogs import GitBlameDialog
            GitBlameDialog(os.path.basename(path), data, self).exec()

    def show_history(self, path):
        rel = os.path.relpath(path, self.repo_path)
        data = self.git_handler.get_file_history(rel)
        if data:
            from core.ui.git_dialogs import GitHistoryDialog
            GitHistoryDialog(os.path.basename(path), data, self).exec()
            
    def set_repository(self, path):
        self.repo_path = path
        if self.git_handler.open_repository(path):
            self.stack.setCurrentWidget(self.repo_widget)
            self.refresh()
        else:
            self.stack.setCurrentWidget(self.no_repo_widget)
