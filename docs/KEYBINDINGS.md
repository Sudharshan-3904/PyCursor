# Keyboard Shortcuts (Keybindings)

PyCursor IDE now includes a comprehensive keybindings system that allows you to customize keyboard shortcuts to match your workflow.

## Features

- **Centralized Management**: All keyboard shortcuts are managed through a single `KeyBindingsManager` class
- **Customizable**: Easily customize any keyboard shortcut through the settings dialog
- **Conflict Detection**: The system automatically detects and warns about conflicting shortcuts
- **Persistent**: Your custom keybindings are saved and loaded automatically
- **Categorized**: Shortcuts are organized by category (File, Edit, View, Navigation, etc.)
- **Reset to Defaults**: Easily reset all shortcuts to their default values

## Default Keyboard Shortcuts

### File Operations
- `Ctrl+O` - Open File
- `Ctrl+K Ctrl+O` - Open Folder
- `Ctrl+S` - Save File
- `Ctrl+Shift+S` - Save As
- `Ctrl+W` - Close Tab
- `Ctrl+N` - New File

### Edit Operations
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+A` - Select All
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+/` - Toggle Line Comment
- `Ctrl+D` - Duplicate Line
- `Ctrl+Shift+K` - Delete Line
- `Alt+Up` - Move Line Up
- `Alt+Down` - Move Line Down

### View Operations
- `Ctrl+B` - Toggle Explorer
- `Ctrl+`` ` - Toggle Terminal
- `Ctrl+Shift+A` - Toggle AI Assistant
- `Ctrl++` - Zoom In
- `Ctrl+-` - Zoom Out
- `Ctrl+0` - Reset Zoom

### Navigation
- `Ctrl+G` - Go to Line
- `Ctrl+Tab` - Next Tab
- `Ctrl+Shift+Tab` - Previous Tab
- `F12` - Go to Definition
- `Alt+Left` - Go Back
- `Alt+Right` - Go Forward

### Run/Debug
- `Ctrl+Shift+R` - Run File
- `F5` - Start Debugging
- `Shift+F5` - Stop Debugging

### AI Features
- `Ctrl+Shift+I` - Open AI Chat
- `Ctrl+Shift+E` - Explain Selected Code

### Terminal
- `Ctrl+Shift+`` ` - New Terminal
- `Ctrl+K` - Clear Terminal

### Application
- `Ctrl+P` - Quick Open File
- `Ctrl+Shift+P` - Show Command Palette
- `Ctrl+,` - Open Settings

## Customizing Keyboard Shortcuts

### Through Settings Dialog

1. Open Settings (`Ctrl+,` or File → Settings)
2. Navigate to the "Keybindings" tab
3. Click "Edit Keyboard Shortcuts"
4. Search for the command you want to customize
5. Click the "Edit" button next to the command
6. Press the new key combination you want to use
7. Click "OK" to save

### Programmatically

You can also customize keybindings programmatically:

```python
from core.utilities.keybindings import KeyBindingsManager

# Get the keybindings manager instance
kb_manager = KeyBindingsManager()

# Update a shortcut
kb_manager.update_shortcut("file.save", "Ctrl+Alt+S")

# Get a shortcut
shortcut = kb_manager.get("file.save")  # Returns "Ctrl+Alt+S"

# Check for conflicts
conflicts = kb_manager.check_conflicts("Ctrl+S")

# Register a new shortcut
kb_manager.register_shortcut("my.custom.action", my_callback_function, widget_context)
```

## Configuration File

Custom keybindings are stored in `config/keybindings.json`. The file format is:

```json
{
  "file.save": {
    "key": "Ctrl+S",
    "description": "Save File",
    "category": "File"
  },
  "edit.undo": {
    "key": "Ctrl+Z",
    "description": "Undo",
    "category": "Edit"
  }
}
```

## Adding New Keybindings

To add a new keybinding to your application:

1. **Define the keybinding** in `core/utilities/keybindings.py`:

```python
DEFAULT_KEYBINDINGS = {
    # ... existing keybindings ...
    "my.new.action": {
        "key": "Ctrl+Shift+N",
        "description": "My New Action",
        "category": "Custom"
    }
}
```

2. **Register the shortcut** in your widget or main window:

```python
def setup_keybindings(self):
    # ... existing registrations ...
    self.keybindings.register_shortcut("my.new.action", self.my_action_handler, self)

def my_action_handler(self):
    # Your action code here
    print("Custom action triggered!")
```

## Best Practices

1. **Use Standard Conventions**: Follow platform conventions (e.g., `Ctrl+S` for Save)
2. **Avoid Conflicts**: Check for conflicts before assigning new shortcuts
3. **Document Custom Shortcuts**: Keep a record of any custom shortcuts you create
4. **Test Thoroughly**: Ensure shortcuts work in all relevant contexts
5. **Provide Alternatives**: Offer menu items or buttons for actions with shortcuts

## Troubleshooting

### Shortcut Not Working

1. Check if the shortcut conflicts with another action
2. Ensure the widget context is correct
3. Verify the shortcut is properly registered
4. Restart the application after making changes

### Resetting to Defaults

If you encounter issues with custom keybindings:

1. Open Settings → Keybindings
2. Click "Reset to Defaults"
3. Restart the application

Alternatively, delete `config/keybindings.json` and restart.

## Technical Details

### Architecture

The keybindings system consists of three main components:

1. **KeyBindingsManager** (`core/utilities/keybindings.py`): Singleton class managing all shortcuts
2. **KeybindingsDialog** (`core/ui/keybindings_dialog.py`): UI for viewing and editing shortcuts
3. **Integration** (`core/app_main.py`): Registration and setup of shortcuts in the main application

### Key Sequence Format

Key sequences use the format: `Modifier+Modifier+Key`

Valid modifiers:
- `Ctrl` - Control key
- `Alt` - Alt key
- `Shift` - Shift key
- `Meta` - Windows/Command key

Examples:
- `Ctrl+S`
- `Ctrl+Shift+P`
- `Alt+F4`
- `Ctrl+K Ctrl+O` (chord sequence)

## Future Enhancements

Planned improvements to the keybindings system:

- [ ] Import/Export keybindings profiles
- [ ] Keybinding presets (VS Code, Sublime Text, etc.)
- [ ] Context-aware shortcuts (editor-only, terminal-only, etc.)
- [ ] Macro recording and playback
- [ ] Visual keybinding cheat sheet
