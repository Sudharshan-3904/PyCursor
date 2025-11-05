# 🧠 PyCursor — AI-Powered IDE Inspired by VS Code

**PyCursor** is a next-generation, AI-powered Integrated Development Environment (IDE) built in **Python**, inspired by **Cursor** and **VS Code**.
It combines the flexibility of a modern code editor with the intelligence of Large Language Models (LLMs) — allowing developers to code faster, smarter, and more intuitively.

---

## 🚀 Features

### 🖥️ VS Code-Style Layout

- Familiar, clean, and modular UI design similar to **Visual Studio Code**.
- Split panes, sidebar, bottom console, and command palette.
- Dockable panels for files, terminals, and extensions.

### 🤖 Extensive LLM Support

- **Dual AI Integration**:

  - **Local LLMs:** Run open models (like _LLaMA 3_, _Mistral_, _Phi-3_, etc.) locally.
  - **API LLMs:** Connect to OpenAI, Anthropic, Gemini, or custom API endpoints.

- **Intelligent features**:

  - Code completion & generation
  - Code explanation and refactoring
  - Inline chat with the model
  - AI-powered documentation and debugging

### 🧰 Full IDE Functionality

- Syntax highlighting and linting (starting with **Python**)
- Built-in terminal and run/debug console
- Project explorer and command palette
- Real-time error reporting and auto-formatting

### 🐍 Python Support (Initial Release)

- Smart autocompletion using AI and static analysis
- Environment-aware interpreter
- Run and debug Python scripts directly inside the IDE
- Future roadmap includes adding support for:

  - JavaScript / TypeScript
  - C++
  - Rust
  - Go
  - And more…

### 🌱 Environment Management

- Integrated **virtual environment** and **conda environment** management.
- Create, activate, and switch environments directly from the UI.
- Detect and manage project dependencies automatically (`requirements.txt`, `pyproject.toml`, etc.)

### ✏️ Code Editing

- Full-featured text editor with:

  - Syntax highlighting
  - Auto-indentation
  - Bracket matching
  - Multi-cursor editing
  - Code folding

- Support for editing multiple files in tabs.

### 🔧 Git & GitHub Integration

- Commit, push, pull, and branch management from within the IDE.
- Visual diff viewer for file changes.
- GitHub authentication and repo cloning support.
- Inline Git blame and history.

### ⌨️ Customizable Keyboard Shortcuts

- Personalize shortcuts for all actions.
- Import/export custom keymaps.
- Default shortcuts inspired by VS Code for an easy transition.

---

## 🏗️ Project Architecture (Planned)

```dir
PyCursor/
│
├── core/
│   ├── ui/                 # Main UI components (panels, layout, editor)
│   ├── ide/                # Core IDE logic (file handling, project mgmt)
│   ├── ai/                 # LLM integrations and prompt engines
│   ├── git/                # Git and GitHub integrations
│   └── env/                # Environment and dependency management
│
├── assets/                 # Icons, themes, fonts
├── extensions/             # Optional plugins and add-ons
├── config/                 # Settings and keybindings
├── tests/                  # Unit and integration tests
└── main.py                 # Entry point of the application
```

---

## ⚙️ Tech Stack

- **Language:** Python 3.10+
- **UI Framework:** PyQt6 / Tkinter / Electron-Python bridge (to be chosen)
- **AI Integration:** OpenAI API, Hugging Face, Ollama, or custom REST endpoints
- **Git Integration:** GitPython
- **Environment Management:** `venv`, `conda`, or `virtualenv`
- **Code Intelligence:** `jedi`, `pyflakes`, `black`, `mypy`, `ruff`

---

## 🧩 Roadmap

| Phase | Feature                       | Status         |
| ----- | ----------------------------- | -------------- |
| 1     | Core Python IDE + Layout      | 🏗️ In Progress |
| 2     | LLM Integration (Local + API) | ⏳ Planned     |
| 3     | Git & GitHub Integration      | ⏳ Planned     |
| 4     | Environment Management UI     | ⏳ Planned     |
| 5     | Multi-language Support        | ⏳ Planned     |
| 6     | Plugin System & Theming       | ⏳ Planned     |

---

## 🛠️ Installation (Development Mode)

```bash
# Clone the repo
git clone https://github.com/yourusername/pycursor.git
cd pycursor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

## 💬 Contributing

Contributions are welcome!
Please fork the repository, create a feature branch, and submit a pull request.

---

## 📄 License

MIT License © 2025 [Your Name]

---

## 🌟 Inspiration

This project draws inspiration from:

- [VS Code](https://code.visualstudio.com/)
- [Cursor](https://cursor.sh/)
- [Spyder IDE](https://www.spyder-ide.org/)
- [JupyterLab](https://jupyter.org/)

---
