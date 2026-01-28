# 🗺️ PyCursor IDE: Comprehensive Phase-based Roadmap

This document serves as the project's Software Requirements Specification (SRS) and developmental guide, structured by implementation phases.

---

## Phase 1: Core Editor & Layout ✅
- **Requirements:**
    - Python 3.10+
    - PyQt6 Core Libraries
    - Operating System: Windows (primary), macOS/Linux support
- **Tasks:**
    - [x] Initialize `QMainWindow` with `QSplitter` for flexible layout management.
    - [x] Implement a File Navigation Sidebar using `QTreeView` and `QFileSystemModel`.
    - [x] Create a log-based Terminal widget.
    - [x] Implement basic File Open/Save/Save As functionality.
- **Challenges:**
    - Synchronizing the file system model with real-time OS changes (Watchdog integration).
    - Managing relative layouts in a resizable window without visual glitches.
- **Added things:**
    - Standard title bar and menu bar.
    - Multi-pane splitting.
    - Base `CodeEditor` class using PyQt6.

---

## Phase 2: Editor Intelligence & UX ✅
- **Requirements:**
    - QScintilla (PyQt6-QScintilla)
    - Pygments (for advanced lexing)
- **Tasks:**
    - [x] Implement syntax highlighting for Python.
    - [x] Add line numbers and a gutter area for code folding.
    - [x] Implement basic auto-indentation and bracket matching logic.
    - [x] Integrate `pyflakes` for real-time syntax checking.
- **Challenges:**
    - Performance lag during real-time linting of large files.
    - Managing Scintilla markers for error highlighting without interfering with selection.
- **Added things:**
    - Collapsible code blocks (Classes/Functions).
    - Highlighted matching brackets `()[]{}`.
    - Inline error squiggles and status bar error reporting.

---

## Phase 3: LLM & AI Integration ✅
- **Requirements:**
    - API Keys for OpenAI, Anthropic, or Gemini.
    - Local Ollama installation (optional but recommended).
    - `langchain` and `httpx` for streaming.
- **Tasks:**
    - [x] Build a unified AI provider manager using the Strategy Pattern.
    - [x] Implement a sidebar AI Chat interface with Markdown rendering.
    - [x] Develop an "Inline AI" system for code generation and refactoring.
    - [x] Implement streaming responses to keep the UI interactive.
- **Challenges:**
    - Handling async network requests without freezing the PyQt GUI thread.
    - Context window management for long files.
- **Added things:**
    - Selective hunk application (Diff-based AI suggestions).
    - Intelligent docstring generator (NumPy/Google styles).
    - Debug hints and error explanations directly from traceback logs.

---

## Phase 4: Git & GitHub Integration ✅
- **Requirements:**
    - `GitPython` library
    - System Git installation
- **Tasks:**
    - [x] Implement a dedicated Git Panel showing staged/unstaged changes.
    - [x] create a visual Diff Viewer for comparing file versions.
    - [x] Implement Git Blame (inline) and file history views.
    - [x] Add support for Commit, Push, Pull, and Branch switching.
- **Challenges:**
    - Parsing complex Git diff outputs into a readable GUI format.
    - Handling merge conflicts within the IDE UI.
- **Added things:**
    - Inline "Blame" labels next to line numbers.
    - Automatic repo detection when opening folders.
    - Visual Git history per line.

---

## Phase 4.5: UX Renewal & Performance Optimization ✅
- **Requirements:**
    - Specialized CSS (QSS) stylesheet.
    - Custom Font assets.
- **Tasks:**
    - [x] Implement the VS Code-style "Activity Bar" for view toggling.
    - [x] Design a unified dark theme (Catppuccin-inspired).
    - [x] Optimize startup by moving AI/Git detection to background threads (`QThread`).
    - [x] Implement a searchable Command Palette (`Ctrl+Shift+P`).
- **Challenges:**
    - Balancing aesthetic rounded corners with PyQt's layout constraints.
    - Thread safety when updating UI components from background Git checks.
- **Added things:**
    - Interactive Keyboard Shortcuts dialog.
    - Modern Status Bar showing Git branch, Encoding, and Line/Col.
    - Fluid animations for sidebar expanding/collapsing.

---

## Phase 5: Python Environment & Dependency Management ✅
- **Requirements:**
    - `virtualenv` or `conda` binaries.
    - `json` configuration storage.
- **Tasks:**
    - [x] Create a manager to detect, create, and switch between virtual environments.
    - [x] Auto-detect `requirements.txt` or `pyproject.toml`.
    - [x] Integrated "Terminal Activation" that automatically syncs the terminal with the IDE's active environment.
- **Challenges:**
    - Standardizing environment activation across different shells (CMD, PowerShell, Bash).
    - Ensuring the AI engine uses the interpreter path from the selected environment.
- **Added things:**
    - Environment selector in the status bar.
    - One-click dependency installation from `requirements.txt`.

---

## Phase 6: Plugin System & Theming ✅
- **Requirements:**
    - Dynamic module loading logic (`importlib`).
    - Extended color palettes.
- **Tasks:**
    - [x] Build a `PluginManager` that loads Python scripts from a `plugins/` directory.
    - [x] Implement a "Light Mode" stylesheet and a global theme toggle.
    - [x] Allow users to install external extensions (VSIX assets).
    - [x] Persistent settings sync using `settings.json`.
- **Challenges:**
    - Creating a safe sandbox or stable API for plugins to interact with the main IDE.
    - Synchronizing the QScintilla lexer colors with the global application theme.
- **Added things:**
    - Full Light/Dark mode support.
    - Marketplace-ready Extensions panel.
    - Customizable keybindings with conflict detection.

---

## Phase 7: Polishing & Deployment ✅
- **Requirements:**
    - `PyInstaller` for packaging.
    - `pytest` and `pytest-qt` for testing.
- **Tasks:**
    - [x] Implement performance warnings for files >5MB.
    - [x] Create a welcoming Onboarding Dialog for new users.
    - [x] Build an automated packaging script (`package.py`).
    - [x] Write unit tests for Editor, AI, and Git components.
- **Challenges:**
    - Resolving Windows-specific file permission errors during Git tests.
    - Reducing the size of the final bundled executable.
- **Added things:**
    - Interactive Welcome screen.
    - Standalone .exe distribution support.
    - High-coverage automated test suite.

---

## Phase 8: Universal Intelligence (LSP) ✅
- **Requirements:**
    - `python-lsp-server` (pylsp)
    - `JSON-RPC` transport layer
- **Tasks:**
    - [x] Implement an LSP Client to communicate with background language servers.
    - [x] Add "Go to Definition", "Find References", and "Workspace Symbols".
    - [x] Implement real-time type checking with Pyright.
- **Challenges:**
    - Managing the lifecycle of a high-memory background process (LSP Server).
    - Synchronizing Scintilla buffer offsets with LSP line/char positions.
- **Added things:**
    - Peek definition overlays.
    - Symbol breadcrumbs at the top of the editor.

---

## Phase 9: Workspace Context (Local RAG) ⏳
- **Requirements:**
    - `faiss-cpu` (Vector DB)
    - `sentence-transformers` (Local Embeddings)
- **Tasks:**
    - Build a background worker to index the current workspace.
    - Implement AST-aware chunking for classes and functions.
    - Integrate vector retrieval into the AI chat prompt.
- **Challenges:**
    - Efficiently re-indexing only the changed files (incremental indexing).
    - Managing RAM usage during large codebase ingestion.
- **Added things:**
    - Global "Chat with Codebase" feature.
    - Automatic context injection for code generation.

---

## Phase 10: The Debugger Engine (DAP) ⏳
- **Requirements:**
    - `debugpy`
    - Debug Adapter Protocol (DAP)
- **Tasks:**
    - Implement a DAP Client to handle breakpoints and execution flow.
    - Build UI panels for "Variables", "Watch", and "Call Stack".
    - Implement step-over, step-into, and pause functionality.
- **Challenges:**
    - Interfacing with the DAP's complex JSON protocol.
    - Visualizing nested Python objects in a performant tree view.
- **Added things:**
    - Inline variable value overlays during debugging.
    - Conditional gutter breakpoints.

---

## Phase 11: Data Science Bridge ⏳
- **Requirements:**
    - `QtWebEngine`
    - `jupyter_client`
- **Tasks:**
    - Create a renderer for `.ipynb` files using HTML/JS templates.
    - Connect to local Jupyter Kernels for cell execution.
    - Implement interactive outputs for plots and tables.
- **Challenges:**
    - Ensuring two-way binding between the JSON notebook file and the UI web engine.
- **Added things:**
    - Integrated Pandas DataFrame explorer.
    - High-DPI Matplotlib plot rendering.

---

## Phase 12: Autonomous Agentic Workflows ⏳
- **Requirements:**
    - `LangChain` / `LangGraph` agents.
    - Tool-calling system (FS, Shell, Search).
- **Tasks:**
    - Develop an "Architect" agent that can plan changes across multiple files.
    - Implement a "Human-in-the-loop" approval UI for file mutations.
    - Autonomous bug-fixing loop (Run tests -> Read error -> Fix -> Repeat).
- **Challenges:**
    - Maintaining agent reliability on complex multi-turn tasks.
    - Protecting user data from destructive autonomous actions.
- **Added things:**
    - Multi-file code generation and refactoring.
    - Automated project scaffolding from prompts.
