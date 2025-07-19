import subprocess
import socket
import json
import threading
import os
import sys, uuid, random


class UIBridge:
    def __init__(self, test_mode, ui_script='ui_menu_files/ui_main.exe', port=22128):
        if test_mode:
            ui_script = 'ui_menu_files/ui_main.py'

        self.socket = None
        self.client_socket = None
        self.ui_process = None
        self._setup_connection(ui_script, port)

    def _setup_connection(self, ui_script, port):
        try:
            self.ui_script = ui_script

            # create server socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('localhost', port))
            self.socket.listen(1)

            # Launch UI process
            if getattr(sys, 'frozen', False):  # If running as exe
                ui_path = os.path.join(os.path.dirname(sys.executable), self.ui_script)
                self.ui_process = subprocess.Popen([ui_path])
            else:
                self.ui_process = subprocess.Popen([sys.executable, self.ui_script])

            # Accept connection (with timeout)
            self.socket.settimeout(1.0)
            self.client_socket, _ = self.socket.accept()
            self.client_socket.settimeout(0.001)  # Non-blocking

        except Exception as e:
            print(f"UI connection failed: {e}")

    def send(self, data):
        if self.client_socket:
            try:
                data["random_number"] = str(random.random())
                message = json.dumps(data) + '\n'
                self.client_socket.send(message.encode())
            except:
                pass

    def receive(self):
        if self.client_socket:
            try:
                data = self.client_socket.recv(1024).decode().strip()
                return json.loads(data) if data else None
            except:
                pass
        return None

    def close(self):
        if self.client_socket:
            self.client_socket.close()
        if self.socket:
            self.socket.close()
        if self.ui_process:
            self.ui_process.terminate()