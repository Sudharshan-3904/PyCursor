"""
PyCursor IDE Bootstrap and Development Lifecycle Entry Point.
Implements a Hot-Reloading system for developers to preview changes in real-time
without manual restarts, while orchestrating the primary QApplication loop.
"""

import sys
import os
import importlib
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QFontInfo

from core import app_main

class ReloadSignals(QObject):
    """
    Message bus for the Hot-Reloading system.
    """
    reload_triggered = pyqtSignal(str) # Emits the path of the modified file

class ReloadHandler(FileSystemEventHandler):
    """
    Monitors the file system for source code modifications.
    Implements debouncing to prevent rapid-fire reload cycles.
    """
    def __init__(self, signals: ReloadSignals):
        super().__init__()
        self.signals = signals
        self.last_reload = 0

    def on_modified(self, event):
        """
        Callback triggered when a disk-level modification is detected.
        """
        if not event.is_directory and event.src_path.endswith(".py"):
            now = time.time()
            # Debounce: Ensure 1-second gap between reloads
            if now - self.last_reload > 1:
                self.last_reload = now
                self.signals.reload_triggered.emit(event.src_path)

class HotReloader(QObject):
    """
    Master controller for the IDE Hot-Reloading mechanism.
    Coordinates component-level re-binding or full application state resets.
    """
    def __init__(self, app: QApplication):
        """
        Initializes the reloader linked to the main event loop.
        """
        super().__init__()
        self.app = app
        self.main_window = None
        self.observer = None
        self.signals = ReloadSignals()
        self.signals.reload_triggered.connect(self._dispatch_reload)

    def start(self):
        """
        Initializes the file system watcher and launches the application.
        """
        watch_root = os.path.abspath(".")
        handler = ReloadHandler(self.signals)
        self.observer = Observer()
        self.observer.schedule(handler, watch_root, recursive=True)
        self.observer.start()

        # Perform initial application launch
        self._reload_full()

    def stop(self):
        """
        Gracefully terminates background monitoring threads.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def _dispatch_reload(self, src_path: str):
        """
        Routes the reload event to either a specific component fix or a full reset.
        """
        rel_path = os.path.relpath(src_path, os.path.abspath(".")).replace("\\", "/")
        print(f"[HotReload] Source Modified: {rel_path}")

        # Components are mapped to their relative paths for targeted reloading
        if rel_path == "core/app_main.py":
            self._reload_full()
        elif rel_path.startswith("core/ui/"):
            # Component-level reloading logic could be placed here
            # Defaulting to full reload for stability in this version
            self._reload_full()
        else:
            self._reload_full()

    def _reload_full(self):
        """
        Performs a deep reload of the core application logic and swaps the main window.
        Preserves global state while refreshing the UI implementation.
        """
        try:
            importlib.reload(app_main)
            old_window = self.main_window
            
            # Instantiate fresh window from updated code
            self.main_window = app_main.PyCursorMain()
            self.main_window.show()
            
            # Clean up old window instances
            if old_window:
                old_window.close()
                old_window.deleteLater()

            print("[HotReload] Application state refreshed successfully.")
        except Exception as e:
            print(f"[HotReload] Error during refresh: {e}")

def main():
    """
    Primary execution entry point for PyCursor IDE.
    """
    qapp = QApplication(sys.argv)
    
    # Set application-wide font to prevent invalid font sizes
    app_font = QFont()
    app_font.setFamily("Times New Roman")
    app_font.setPixelSize(-1)
    app_font.setPointSize(11)
    qapp.setFont(app_font)
    
    # Initialize the Hot-Reloader which manages the PyCursorMain instance
    reloader = HotReloader(qapp)
    reloader.start()

    try:
        status = qapp.exec()
    finally:
        reloader.stop()

    sys.exit(status)

if __name__ == "__main__":
    main()
