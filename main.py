import sys
import os
import importlib
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core import app_main

from core.ui.editor import CodeEditor
from core.ui.terminal import Terminal
from core.ui.sidebar import SideBar


class ReloadSignals(QObject):
    reload_triggered = pyqtSignal(object)


class ReloadHandler(FileSystemEventHandler):
    """Watchdog handler to detect file changes."""

    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.last_reload = 0

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            current_time = time.time()
            if current_time - self.last_reload > 1:
                self.last_reload = current_time
                self.signals.reload_triggered.emit(event.src_path)


class HotReloader(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.window = None
        self.observer = None
        self.signals = ReloadSignals()
        self.signals.reload_triggered.connect(self._handle_reload)

        self.component_map = {
            "core/ui/editor.py": self._reload_editor,
            "core/ui/terminal.py": self._reload_terminal,
            "core/ui/sidebar.py": self._reload_sidebar,
            "core/app_main.py": self._reload_full,
        }

    def start(self):
        """Start the file observer."""
        watch_path = os.path.abspath(".")
        print(f"[HotReload] Watching for changes in: {watch_path}")

        event_handler = ReloadHandler(self.signals)
        self.observer = Observer()
        self.observer.schedule(event_handler, watch_path, recursive=True)
        self.observer.start()

        self._reload_full()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def _handle_reload(self, src_path):
        """Figure out which component to reload."""
        project_root = os.path.abspath(".")
        rel_path = os.path.relpath(src_path, project_root).replace("\\", "/")
        print(f"[HotReload] Detected change: {rel_path}")

        for path, func in self.component_map.items():
            if path == rel_path:
                func()
                break
        else:
            self._reload_full()

    def _reload_editor(self):
        try:
            import core.ui.editor as editor_module
            importlib.reload(editor_module)

            if self.window:
                for i in range(self.window.tab_widget.count()):
                    widget = self.window.tab_widget.widget(i)
                    if isinstance(widget, CodeEditor):
                        content = widget.toPlainText()
                        cursor_pos = widget.textCursor().position()
                        file_path = getattr(widget, "file_path", None)

                        widget.__class__ = editor_module.CodeEditor
                        widget.setPlainText(content)
                        cursor = widget.textCursor()
                        cursor.setPosition(cursor_pos)
                        widget.setTextCursor(cursor)
                        if file_path:
                            widget.file_path = file_path

            print("[HotReload] Editor reloaded")
        except Exception as e:
            print(f"[HotReload] Editor reload failed: {e}")

    def _reload_terminal(self):
        try:
            import core.ui.terminal as terminal_module
            importlib.reload(terminal_module)

            if self.window:
                term = self.window.terminal
                term.__class__ = terminal_module.Terminal
                term.keyPressEvent = terminal_module.Terminal.keyPressEvent.__get__(term)
                term._on_output = terminal_module.Terminal._on_output.__get__(term)
                term._detect_shell = terminal_module.Terminal._detect_shell.__get__(term)
                term._get_env_activation_path = terminal_module.Terminal._get_env_activation_path.__get__(term)
                term.log = terminal_module.Terminal.log.__get__(term)

            print("[HotReload] Terminal reloaded (process preserved)")
        except Exception as e:
            print(f"[HotReload] Terminal reload failed: {e}")

    def _reload_sidebar(self):
        try:
            import core.ui.sidebar as sidebar_module
            importlib.reload(sidebar_module)

            if self.window:
                old_sidebar = self.window.sidebar
                old_sidebar.__class__ = sidebar_module.SideBar
                old_sidebar.setRootPath(old_sidebar.rootPath())

            print("[HotReload] Sidebar reloaded")
        except Exception as e:
            print(f"[HotReload] Sidebar reload failed: {e}")

    def _reload_full(self):
        try:
            importlib.reload(app_main)
            if self.window:
                old_window = self.window
                self.window = app_main.PyCursorMain()
                self.window.show()
                old_window.close()
                old_window.deleteLater()
            else:
                self.window = app_main.PyCursorMain()
                self.window.show()

            print("[HotReload] Full reload completed")
        except Exception as e:
            print(f"[HotReload] Full reload failed: {e}")


def main():
    app = QApplication(sys.argv)
    reloader = HotReloader(app)
    reloader.start()

    try:
        exit_code = app.exec()
    finally:
        reloader.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
