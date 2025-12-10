"""
Git Integration Module for PyCursor IDE

Provides Git operations using GitPython library.
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GitFileStatus:
    """Represents the status of a file in Git"""
    path: str
    status: str  # 'modified', 'added', 'deleted', 'untracked', 'renamed'
    staged: bool


@dataclass
class GitCommit:
    """Represents a Git commit"""
    sha: str
    author: str
    email: str
    date: datetime
    message: str
    short_sha: str


class GitHandler:
    """Handles all Git operations for the IDE"""
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path
        self.repo = None
        
        if repo_path:
            self.open_repository(repo_path)
    
    def open_repository(self, path: str) -> bool:
        """Open a Git repository"""
        try:
            import git
            self.repo = git.Repo(path, search_parent_directories=True)
            self.repo_path = self.repo.working_dir
            return True
        except Exception as e:
            print(f"Failed to open repository: {e}")
            return False
    
    def is_repository(self, path: str) -> bool:
        """Check if a path is a Git repository"""
        try:
            import git
            git.Repo(path, search_parent_directories=True)
            return True
        except:
            return False
    
    def init_repository(self, path: str) -> bool:
        """Initialize a new Git repository"""
        try:
            import git
            self.repo = git.Repo.init(path)
            self.repo_path = path
            return True
        except Exception as e:
            print(f"Failed to initialize repository: {e}")
            return False
    
    def get_status(self) -> List[GitFileStatus]:
        """Get the status of all files in the repository"""
        if not self.repo:
            return []
        
        files = []
        
        # Staged files
        for item in self.repo.index.diff("HEAD"):
            files.append(GitFileStatus(
                path=item.a_path,
                status='modified' if item.change_type == 'M' else item.change_type.lower(),
                staged=True
            ))
        
        # Unstaged files
        for item in self.repo.index.diff(None):
            files.append(GitFileStatus(
                path=item.a_path,
                status='modified' if item.change_type == 'M' else item.change_type.lower(),
                staged=False
            ))
        
        # Untracked files
        for file in self.repo.untracked_files:
            files.append(GitFileStatus(
                path=file,
                status='untracked',
                staged=False
            ))
        
        return files
    
    def stage_file(self, file_path: str) -> bool:
        """Stage a file for commit"""
        try:
            self.repo.index.add([file_path])
            return True
        except Exception as e:
            print(f"Failed to stage file: {e}")
            return False
    
    def unstage_file(self, file_path: str) -> bool:
        """Unstage a file"""
        try:
            self.repo.index.reset([file_path])
            return True
        except Exception as e:
            print(f"Failed to unstage file: {e}")
            return False
    
    def stage_all(self) -> bool:
        """Stage all changes"""
        try:
            self.repo.git.add(A=True)
            return True
        except Exception as e:
            print(f"Failed to stage all: {e}")
            return False
    
    def commit(self, message: str, author_name: Optional[str] = None, 
               author_email: Optional[str] = None) -> bool:
        """Commit staged changes"""
        try:
            if author_name and author_email:
                actor = f"{author_name} <{author_email}>"
                self.repo.index.commit(message, author=actor, committer=actor)
            else:
                self.repo.index.commit(message)
            return True
        except Exception as e:
            print(f"Failed to commit: {e}")
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current branch"""
        try:
            return self.repo.active_branch.name
        except:
            return None
    
    def get_branches(self) -> List[str]:
        """Get all local branches"""
        try:
            return [branch.name for branch in self.repo.branches]
        except:
            return []
    
    def get_remote_branches(self) -> List[str]:
        """Get all remote branches"""
        try:
            branches = []
            for ref in self.repo.remotes.origin.refs:
                branches.append(ref.name.replace('origin/', ''))
            return branches
        except:
            return []
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch"""
        try:
            self.repo.create_head(branch_name)
            return True
        except Exception as e:
            print(f"Failed to create branch: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout a branch"""
        try:
            self.repo.git.checkout(branch_name)
            return True
        except Exception as e:
            print(f"Failed to checkout branch: {e}")
            return False
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """Delete a branch"""
        try:
            self.repo.delete_head(branch_name, force=force)
            return True
        except Exception as e:
            print(f"Failed to delete branch: {e}")
            return False
    
    def pull(self, remote: str = 'origin', branch: Optional[str] = None) -> Tuple[bool, str]:
        """Pull changes from remote"""
        try:
            if branch is None:
                branch = self.get_current_branch()
            
            result = self.repo.remotes[remote].pull(branch)
            return True, "Pull successful"
        except Exception as e:
            return False, str(e)
    
    def push(self, remote: str = 'origin', branch: Optional[str] = None, 
             set_upstream: bool = False) -> Tuple[bool, str]:
        """Push changes to remote"""
        try:
            if branch is None:
                branch = self.get_current_branch()
            
            if set_upstream:
                self.repo.git.push('--set-upstream', remote, branch)
            else:
                self.repo.remotes[remote].push(branch)
            
            return True, "Push successful"
        except Exception as e:
            return False, str(e)
    
    def fetch(self, remote: str = 'origin') -> bool:
        """Fetch from remote"""
        try:
            self.repo.remotes[remote].fetch()
            return True
        except Exception as e:
            print(f"Failed to fetch: {e}")
            return False
    
    def get_commits(self, max_count: int = 50) -> List[GitCommit]:
        """Get recent commits"""
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
        except:
            return []
    
    def get_file_diff(self, file_path: str, staged: bool = False) -> Optional[str]:
        """Get diff for a specific file"""
        try:
            if staged:
                diff = self.repo.git.diff('--staged', file_path)
            else:
                diff = self.repo.git.diff(file_path)
            return diff
        except Exception as e:
            print(f"Failed to get diff: {e}")
            return None
    
    def get_file_blame(self, file_path: str) -> List[Dict]:
        """Get blame information for a file"""
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
        except Exception as e:
            print(f"Failed to get blame: {e}")
            return []
    
    def get_file_history(self, file_path: str, max_count: int = 20) -> List[GitCommit]:
        """Get commit history for a specific file"""
        try:
            commits = []
            for commit in self.repo.iter_commits(paths=file_path, max_count=max_count):
                commits.append(GitCommit(
                    sha=commit.hexsha,
                    short_sha=commit.hexsha[:7],
                    author=commit.author.name,
                    email=commit.author.email,
                    date=datetime.fromtimestamp(commit.committed_date),
                    message=commit.message.strip()
                ))
            return commits
        except:
            return []
    
    def clone_repository(self, url: str, path: str, progress_callback=None) -> bool:
        """Clone a repository from URL"""
        try:
            import git
            if progress_callback:
                git.Repo.clone_from(url, path, progress=progress_callback)
            else:
                git.Repo.clone_from(url, path)
            self.open_repository(path)
            return True
        except Exception as e:
            print(f"Failed to clone repository: {e}")
            return False
    
    def get_remotes(self) -> List[str]:
        """Get all remote names"""
        try:
            return [remote.name for remote in self.repo.remotes]
        except:
            return []
    
    def add_remote(self, name: str, url: str) -> bool:
        """Add a new remote"""
        try:
            self.repo.create_remote(name, url)
            return True
        except Exception as e:
            print(f"Failed to add remote: {e}")
            return False
    
    def remove_remote(self, name: str) -> bool:
        """Remove a remote"""
        try:
            self.repo.delete_remote(name)
            return True
        except Exception as e:
            print(f"Failed to remove remote: {e}")
            return False
    
    def discard_changes(self, file_path: str) -> bool:
        """Discard changes in a file"""
        try:
            self.repo.git.checkout('--', file_path)
            return True
        except Exception as e:
            print(f"Failed to discard changes: {e}")
            return False
    
    def get_config(self, key: str) -> Optional[str]:
        """Get a Git config value"""
        try:
            return self.repo.config_reader().get_value('user', key)
        except:
            return None
    
    def set_config(self, section: str, key: str, value: str) -> bool:
        """Set a Git config value"""
        try:
            with self.repo.config_writer() as config:
                config.set_value(section, key, value)
            return True
        except Exception as e:
            print(f"Failed to set config: {e}")
            return False
