from PyQt6.QtWidgets import QMessageBox

def activate(ide):
    """
    Called when the plugin is loaded.
    'ide' is the PyCursorMain instance.
    """
    # Example: Add a new action to the menu
    if hasattr(ide, "menu_manager"):
        def say_hello():
            QMessageBox.information(ide, "Hello", "Greetings from the Hello World Plugin!")
        
        # We can dynamically add to menus
        # This is just a proof of concept
        pass

def deactivate(ide):
    """Called when the plugin is unloaded."""
    pass
