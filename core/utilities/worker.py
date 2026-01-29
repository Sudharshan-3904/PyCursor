from PyQt6.QtCore import QThread, pyqtSignal
import traceback

class WorkerThread(QThread):
    """
    Asynchronous concurrency wrapper for executing blocking operations without freezing the UI.
    Generic implementation that can wrap any callable and emit signals on completion or failure.
    """
    # Signals for lifecycle and result communication
    result_ready = pyqtSignal(object)  # Emitted with the return value of func
    error_occurred = pyqtSignal(str)   # Emitted with the stringified exception if func fails
    finished = pyqtSignal()            # Always emitted after execution concludes

    def __init__(self, func, *args, **kwargs):
        """
        Initializes the thread with a target function and its arguments.
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Overridden execution entry point. Calls the wrapped function and manages signaling.
        """
        try:
            # Execute target callable with captured context
            result = self.func(*self.args, **self.kwargs) if (self.args or self.kwargs) else self.func()
            self.result_ready.emit(result)
        except Exception as e:
            # Extract traceback and notify the main thread of the failure
            log_msg = f"WorkerThread Exception: {e}\n{traceback.format_exc()}"
            print(log_msg)
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()
