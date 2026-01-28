"""
Git Backend Integration Layer for PyCursor IDE.
Wraps the GitPython library to provide high-level abstractions for repository operations 
including staging, committing, branching, and remote synchronization.
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GitFileStatus:
    """
    Data container for file state within a Git-tracked project.
    """
    path: str
    status: str  # Literal: 'modified', 'added', 'deleted', 'untracked', 'renamed'
    staged: bool

@dataclass
class GitCommit:
    """
    Data container representing a specific Git history entry.
    """
    sha: str
    author: str
    email: str
    date: datetime
    message: str
    short_sha: str

class GitHandler:
    """
    Primary interface for interacting with the Git binary via GitPython.
    Manages repository state and orchestrates standard SCM workflows.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initializes the handler and attempts to open a repository if a path is provided.
        """
        self.repo_path = repo_path
        self.repo = None
        
        if repo_path:
            self.open_repository(repo_path)
    
    def open_repository(self, path: str) -> bool:
        """
        Attempts to bind to an existing Git repository at the specified path.
        """
        try:
            import git
            self.repo = git.Repo(path, search_parent_directories=True)
            self.repo_path = self.repo.working_dir
            return True
        except Exception:
            return False
    
    def is_repository(self, path: str) -> bool:
        """
        Validates if a directory is part of a Git repository.
        """
        try:
            import git
            git.Repo(path, search_parent_directories=True)
            return True
        except Exception:
            return False
    
    def init_repository(self, path: str) -> bool:
        """
        Initializes a new Git repository in the target directory.
        """
        try:
            import git
            self.repo = git.Repo.init(path)
            self.repo_path = path
            return True
        except Exception:
            return False
    
    def get_status(self) -> List[GitFileStatus]:
        """
        Retrieves a comprehensive list of all changed, staged, and untracked files.
        """
        if not self.repo:
            return []
        
        files = []
        
        # Parse Index/HEAD differences (Staged)
        for item in self.repo.index.diff("HEAD"):
            files.append(GitFileStatus(
                path=item.a_path,
                status=item.change_type.lower(),
                staged=True
            ))
        
        # Parse Working-Tree/Index differences (Changed)
        for item in self.repo.index.diff(None):
            files.append(GitFileStatus(
                path=item.a_path,
                status=item.change_type.lower(),
                staged=False
            ))
        
        # Include new files not yet tracked
        for file in self.repo.untracked_files:
            files.append(GitFileStatus(
                path=file,
                status='untracked',
                staged=False
            ))
        
        return files
    
    def stage_file(self, file_path: str) -> bool:
        """
        Adds a file to the Git index (Staged).
        """
        try:
            self.repo.index.add([file_path])
            return True
        except Exception:
            return False
    
    def unstage_file(self, file_path: str) -> bool:
        """
        Removes a file from the index while preserving working tree changes.
        """
        try:
            self.repo.index.reset([file_path])
            return True
        except Exception:
            return False
    
    def stage_all(self) -> bool:
        """
        Stages all current modifications into the index.
        """
        try:
            self.repo.git.add(A=True)
            return True
        except Exception:
            return False
    
    def commit(self, message: str) -> bool:
        """
        Creates a new commit from the currently staged changes.
        """
        try:
            self.repo.index.commit(message)
            return True
        except Exception:
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """
        Returns the active branch name.
        """
        try:
            return self.repo.active_branch.name
        except Exception:
            return None
    
    def get_branches(self) -> List[str]:
        """
        Lists all local heads/branches.
        """
        try:
            return [branch.name for branch in self.repo.branches]
        except Exception:
            return []
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Switches the local working tree to the specified branch.
        """
        try:
            self.repo.git.checkout(branch_name)
            return True
        except Exception:
            return False
    
    def get_commits(self, max_count: int = 50) -> List[GitCommit]:
        """
        Parses the project commit history into GitCommit objects.
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append(GitCommit(
                    sha=commit.hexsha,
                    short_sha=commit.hexsha[:7],
                    author=commit.author.name,
                    email=commit.author.email,
                    date=datetime.fromtimestamp(commit.committed_date),
                    message=commit.message.strip()
                ))
            return commits
        except Exception:
            return []
    
    def get_file_blame(self, file_path: str) -> List[Dict]:
        """
        Generates line-by-line attribution of changes for a target file.
        """
        try:
            blame_data = []
            for commit, lines in self.repo.blame('HEAD', file_path):
                for line in lines:
                    blame_data.append({
                        'commit': commit.hexsha[:7],
                        'author': commit.author.name,
                        'date': datetime.fromtimestamp(commit.committed_date),
                        'line': line
                    })
            return blame_data
        except Exception:
            return []
    
    def discard_changes(self, file_path: str) -> bool:
        """
        Reverts working tree modifications for a file by checking it out from HEAD.
        """
        try:
            self.repo.git.checkout('--', file_path)
            return True
        except Exception:
            return False
