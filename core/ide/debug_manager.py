import json
import socket
import threading
import subprocess
import os
from PyQt6.QtCore import QObject, pyqtSignal

class DebugManager(QObject):
    """
    Manages debugging sessions using the Debug Adapter Protocol (DAP).
    Communicates with debugpy to provide breakpoints, stepping, and variable inspection.
    """
    stopped = pyqtSignal(dict)
    continued = pyqtSignal()
    output_received = pyqtSignal(str)
    
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.process = None
        self.socket = None
        self.request_id = 1
        self.callbacks = {}
        self.breakpoints = {} # {file_path: [lines]}

    def start_session(self, script_path):
        """
        Launches debugpy and connects the DAP client.
        """
        port = 5678
        env = os.environ.copy()
        env["PYTHONPATH"] = self.project_path
        
        cmd = [
            "python", "-m", "debugpy", 
            "--listen", f"127.0.0.1:{port}",
            "--wait-for-client",
            script_path
        ]
        
        self.process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Connect socket
        threading.Thread(target=self._connect_and_listen, args=(port,), daemon=True).start()

    def _connect_and_listen(self, port):
        import time
        for _ in range(10):
            try:
                self.socket = socket.create_connection(("127.0.0.1", port))
                break
            except ConnectionRefusedError:
                time.sleep(0.5)
        
        if self.socket:
            self._initialize_dap()
            self._read_loop()

    def _initialize_dap(self):
        self.send_request("initialize", {
            "clientID": "pycursor",
            "adapterID": "python",
            "pathFormat": "path",
            "linesStartAt1": True,
            "columnsStartAt1": True,
            "supportsVariableType": True
        })

    def send_request(self, command, arguments=None, callback=None):
        rid = self.request_id
        self.request_id += 1
        if callback: self.callbacks[rid] = callback
        
        message = {
            "seq": rid,
            "type": "request",
            "command": command,
            "arguments": arguments or {}
        }
        self._send(message)
        return rid

    def _send(self, message):
        body = json.dumps(message)
        framed = f"Content-Length: {len(body)}\r\n\r\n{body}"
        self.socket.sendall(framed.encode("utf-8"))

    def _read_loop(self):
        while self.socket:
            try:
                # Basic framing parser (simplified)
                data = self.socket.recv(4096).decode("utf-8")
                if not data: break
                if "{" in data:
                    body = data[data.find("{"):]
                    self._handle_message(json.loads(body))
            except Exception:
                break

    def _handle_message(self, message):
        m_type = message.get("type")
        if m_type == "response":
            rid = message.get("request_seq")
            if rid in self.callbacks:
                self.callbacks[rid](message.get("body"))
                del self.callbacks[rid]
        elif m_type == "event":
            event = message.get("event")
            if event == "stopped":
                self.stopped.emit(message.get("body"))
            elif event == "continued":
                self.continued.emit()
            elif event == "output":
                self.output_received.emit(message.get("body", {}).get("output", ""))

    def set_breakpoints(self, file_path, lines):
        self.breakpoints[file_path] = lines
        self.send_request("setBreakpoints", {
            "source": {"path": file_path},
            "breakpoints": [{"line": l} for l in lines]
        })

    def step_over(self):
        self.send_request("next", {"threadId": 1})

    def step_into(self):
        self.send_request("stepIn", {"threadId": 1})

    def stop_session(self):
        self.send_request("disconnect", {"restart": False})
        if self.process:
            self.process.terminate()
