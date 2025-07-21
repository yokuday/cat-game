import subprocess
import socket
import json
import threading
import os
import sys, uuid, random
import time
from collections import deque


class UIBridge:
    def __init__(self, test_mode, ui_script='ui_menu_files/ui_main.exe', port=22128):
        if test_mode:
            ui_script = 'ui_menu_files/ui_main.py'

        self.socket = None
        self.client_socket = None
        self.ui_process = None
        self.pending_messages = deque()  # Queue to store unsent messages
        self.retry_thread = None
        self.should_retry = True
        self._setup_connection(ui_script, port)
        self._start_retry_thread()

        self.prepared_data = {}

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

    def _start_retry_thread(self):
        """Start the background thread that retries sending pending messages"""
        self.retry_thread = threading.Thread(target=self._retry_pending_messages, daemon=True)
        self.retry_thread.start()

    def _retry_pending_messages(self):
        """Background thread function that retries sending pending messages every 0.5 seconds"""
        while self.should_retry:
            if self.pending_messages and self.client_socket:
                # Try to send all pending messages
                messages_to_remove = []
                for i, data in enumerate(self.pending_messages):
                    if self._send_direct(data):
                        messages_to_remove.append(i)
                    else:
                        break  # If one fails, stop trying (connection might be broken)

                # Remove successfully sent messages (in reverse order to maintain indices)
                for i in reversed(messages_to_remove):
                    del self.pending_messages[i]

            time.sleep(0.2)

    def _send_direct(self, data):
        """Internal method to actually send data without queuing"""
        if self.client_socket:
            try:
                data["random_number"] = str(random.random())
                message = json.dumps(data) + '\n'
                self.client_socket.send(message.encode())
                return True
            except:
                return False
        return False

    def send(self):
        """Send data immediately if possible, otherwise queue it for retry"""
        # Make a copy of the data to avoid modifying the original
        if self.prepared_data != {}:
            data_copy = self.prepared_data.copy()
            self.prepared_data = {}

            if self.client_socket and self._send_direct(data_copy):
                # Successfully sent immediately
                return
            else:
                # Add to pending messages queue
                self.pending_messages.append(data_copy)

    def prepare_to_send(self, data):
        self.prepared_data = {**self.prepared_data, **data}

    def receive(self):
        if self.client_socket:
            try:
                data = self.client_socket.recv(1024).decode().strip()
                return json.loads(data) if data else None
            except:
                pass
        return None

    def close(self):
        self.should_retry = False  # Stop the retry thread
        if self.retry_thread:
            self.retry_thread.join(timeout=1.0)  # Wait for thread to finish

        if self.client_socket:
            self.client_socket.close()
        if self.socket:
            self.socket.close()
        if self.ui_process:
            self.ui_process.terminate()

    def get_pending_message_count(self):
        """Utility method to check how many messages are pending"""
        return len(self.pending_messages)