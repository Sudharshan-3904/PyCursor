from PyQt6.QtCore import QThread, pyqtSignal
import traceback

class WorkerThread(QThread):
    """
    Generic worker thread for running blocking tasks in the background.
    """
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            if self.args or self.kwargs:
                result = self.func(*self.args, **self.kwargs)
            else:
                result = self.func()
            self.result_ready.emit(result)
        except Exception as e:
            print(f"WorkerThread Error: {e}")
            traceback.print_exc()
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()
