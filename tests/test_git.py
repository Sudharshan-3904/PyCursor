import pytest
import os
import shutil
import tempfile
from core.git.git_handler import GitHandler
from git import Repo

@pytest.fixture
def temp_repo():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    # Initialize a git repo
    repo = Repo.init(temp_dir)
    # Create a dummy file
    file_path = os.path.join(temp_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("test")
    repo.index.add([file_path])
    repo.index.commit("Initial commit")
    
    yield temp_dir
    
    # Cleanup: Close any open handles before deleting
    # In a real scenario, we'd need to ensure GitHandler or Repo objects are closed
    # For testing, we just try our best on Windows
    try:
        shutil.rmtree(temp_dir)
    except:
        # On Windows, sometimes git locks files. 
        # In a test, we can move on if cleanup fails, or use a more robust rmtree
        pass

def test_git_detection(temp_repo):
    handler = GitHandler(temp_repo)
    assert handler.is_repository(temp_repo) == True

def test_git_history(temp_repo):
    handler = GitHandler(temp_repo)
    handler.open_repository(temp_repo)
    history = handler.get_file_history("test.txt")
    assert len(history) >= 1
    assert "Initial commit" in history[0].message

def test_git_status(temp_repo):
    handler = GitHandler(temp_repo)
    handler.open_repository(temp_repo)
    
    # Modify file
    file_path = os.path.join(temp_repo, "test.txt")
    with open(file_path, "a") as f:
        f.write("\nnew line")
        
    status = handler.get_status()
    found = False
    for change in status:
        if change.path == "test.txt" and change.status == 'modified':
            found = True
            break
    assert found
