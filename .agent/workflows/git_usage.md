---
description: How to use Git integration features in PyCursor IDE
---

# Git Integration Workflow

## 1. Opening the Git Panel
- Click the **Source Control** icon (Git logo) in the Activity Bar (left side).
- Or use the keyboard shortcut (default: check Keybindings).

## 2. Initializing a Repository
- If the current folder is not a Git repository, the Git Panel will show "No Git Repository".
- Click **Initialize Repository** to create a new `.git` repo in the current folder.
- Click **Clone Repository** to clone a remote repo into the current folder.

## 3. Staging and Committing
- **Changes** section shows modified, added, deleted files.
- **Stage**: Right-click a file and select "Stage", or click "Stage All".
- **Unstage**: Right-click a staged file and select "Unstage", or click "Unstage All".
- **Commit**: Enter a message in the text box and click **Commit**.

## 4. Branch Management
- The dropdown at the top shows the current branch.
- Click the dropdown to switch branches.
- (Future: Add "Create Branch" button).

## 5. Remote Operations
- **Pull**: Click the "Pull" button to fetch and merge changes from remote.
- **Push**: Click the "Push" button to send commits to remote.
- **Fetch**: Click the "Fetch" button to update remote refs.

## 6. Viewing Diffs
- Right-click a file in the Changes list and select **View Diff**.
- A dialog will open showing the changes with syntax highlighting.
- Green lines are additions, red lines are deletions.

## 7. Git Blame and History
- Open a file in the editor.
- Right-click anywhere in the editor.
- Select **Git Blame** to see who modified each line.
- Select **Git History** to see the commit history of the file.
