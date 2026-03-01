"""
Language Server Protocol (LSP) Integration Module.
Implements a client for communicating with external language servers (like pylsp)
using JSON-RPC over standard I/O streams. Provides features like jump-to-definition.
"""

import json
import socket
import threading
import subprocess
import time
import os
from PyQt6.QtCore import QObject, pyqtSignal

class LSPClient(QObject):
    """
    Low-level client for managing the lifecycle and messaging of an LSP server process.
    Handles JSON-RPC message framing and dispatching.
    """
    notification_received = pyqtSignal(str, dict)
    response_received = pyqtSignal(int, dict)
    error_received = pyqtSignal(int, dict)

    def __init__(self, server_command=None):
        """
        Initializes the client with the command used to launch the server process.
        """
        super().__init__()
        self.server_command = server_command or ["pylsp"]
        self.process = None
        self.request_id = 1
        self.callbacks = {}
        self.is_running = False
        self.send_queue = None

    def start(self) -> bool:
        """
        Launches the LSP server process and starts the asynchronous read loops.
        """
        try:
            import queue
            self.send_queue = queue.Queue()
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            self.is_running = True
            
            # Start background threads for I/O orchestration
            threading.Thread(target=self._read_loop, daemon=True, name="LSP-Read").start()
            threading.Thread(target=self._write_loop, daemon=True, name="LSP-Write").start()
            threading.Thread(target=self._error_loop, daemon=True, name="LSP-Error").start()
            return True
        except Exception as e:
            print(f"LSP Process Error: {e}")
            return False

    def stop(self):
        """
        Gracefully terminates the LSP server process.
        """
        self.is_running = False
        if self.process:
            self.process.terminate()

    def send_request(self, method: str, params: dict, callback=None) -> int:
        """
        Sends a JSON-RPC request and registers a callback for the response.
        """
        rid = self.request_id
        self.request_id += 1
        if callback: self.callbacks[rid] = callback
        
        request = {
            "jsonrpc": "2.0",
            "id": rid,
            "method": method,
            "params": params
        }
        self._send(request)
        return rid

    def send_notification(self, method: str, params: dict):
        """
        Sends a JSON-RPC notification (no response expected).
        """
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self._send(notification)

    def _send(self, data: dict):
        """
        Enqueues a message for the background write thread.
        """
        if self.send_queue:
            self.send_queue.put(data)

    def _write_loop(self):
        """
        Consumes the write queue and pushes data to STDIN.
        """
        while self.is_running:
            try:
                import queue
                data = self.send_queue.get(timeout=0.5)
                if not self.process or not self.process.stdin: continue
                
                body = json.dumps(data)
                content = f"Content-Length: {len(body)}\r\n\r\n{body}"
                self.process.stdin.write(content.encode("utf-8"))
                self.process.stdin.flush()
                self.send_queue.task_done()
            except (queue.Empty, BrokenPipeError, AttributeError):
                continue
            except Exception as e:
                print(f"LSP Write Error: {e}")
                break

    def _read_loop(self):
        """
        Dedicated thread loop for parsing the LSP stream and extracting JSON messages.
        """
        while self.is_running:
            try:
                line = self.process.stdout.readline().decode("utf-8")
                if not line: break
                
                # Parse LSP Message Headers
                if line.startswith("Content-Length: "):
                    length = int(line[16:].strip())
                    while line.strip(): # Skip remaining headers
                        line = self.process.stdout.readline().decode("utf-8")
                    
                    # Read framed body and dispatch
                    body = self.process.stdout.read(length).decode("utf-8")
                    self._handle_incoming_data(json.loads(body))
            except Exception:
                break

    def _error_loop(self):
        """
        Monitors the server STDERR for diagnostic information.
        """
        while self.is_running:
            try:
                line = self.process.stderr.readline().decode("utf-8")
                if not line: break
            except:
                break

    def _handle_incoming_data(self, data: dict):
        """
        Dispatches incoming JSON objects to appropriate handlers based on their type (Result, Error, Notification).
        """
        if "id" in data:
            rid = data["id"]
            if "result" in data:
                if rid in self.callbacks:
                    self.callbacks[rid](data["result"])
                    del self.callbacks[rid]
                self.response_received.emit(rid, data["result"])
            elif "error" in data:
                self.error_received.emit(rid, data["error"])
        elif "method" in data:
            self.notification_received.emit(data["method"], data.get("params", {}))

class LSPManager(QObject):
    """
    High-level manager that provides IDE-specific abstractions over the LSP Client.
    Handles server initialization and project URI mapping.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.client = LSPClient()
        self.initialized = False

    def start(self):
        """
        Begins the LSP session and transmits initialize capabilities.
        """
        if self.client.start():
            root_uri = f"file:///{self.main_window.project_path.replace('\\', '/')}"
            self.client.send_request("initialize", {
                "processId": os.getpid(),
                "rootUri": root_uri,
                "capabilities": {
                    "textDocument": {
                        "definition": {"dynamicRegistration": True}
                    }
                }
            }, self._on_server_ready)

    def _on_server_ready(self, result):
        """
        Finalizes initialization handshake with the server.
        """
        self.initialized = True
        self.client.send_notification("initialized", {})
        
        # Start health check timer
        self.health_timer = threading.Timer(10.0, self.check_health)
        self.health_timer.daemon = True
        self.health_timer.start()

    def check_health(self):
        """
        Periodic check to ensure the server process is alive.
        Restarts the server if it has terminated unexpectedly.
        """
        if not self.client.is_running: return
        
        if self.client.process and self.client.process.poll() is not None:
            print("[LSP] Server process lost. Restarting...")
            self.initialized = False
            self.start()
        else:
            # Reschedule next check
            self.health_timer = threading.Timer(10.0, self.check_health)
            self.health_timer.daemon = True
            self.health_timer.start()

    def get_definition(self, file_path, line, col, callback):
        """
        Requests the definition location for a symbol at the specified coordinates.
        """
        if not self.initialized: return
        uri = f"file:///{file_path.replace('\\', '/')}"
        self.client.send_request("textDocument/definition", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": col}
        }, callback)

    def get_completion(self, file_path, line, col, callback):
        """
        Requests code completion suggestions at the specified coordinates.
        """
        if not self.initialized: return
        uri = f"file:///{file_path.replace('\\', '/')}"
        self.client.send_request("textDocument/completion", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": col}
        }, callback)

    def get_hover(self, file_path, line, col, callback):
        """
        Requests hover documentation for the symbol at the specified coordinates.
        """
        if not self.initialized: return
        uri = f"file:///{file_path.replace('\\', '/')}"
        self.client.send_request("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": col}
        }, callback)

    def get_signature_help(self, file_path, line, col, callback):
        """
        Requests function signature information at the specified coordinates.
        """
        if not self.initialized: return
        uri = f"file:///{file_path.replace('\\', '/')}"
        self.client.send_request("textDocument/signatureHelp", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": col}
        }, callback)
