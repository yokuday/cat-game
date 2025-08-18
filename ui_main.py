import socket
import json
import threading

import pyray as pr
from ui_menu_files.ui_window import Window

import random


class GameUI():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('localhost', 22128))

        threading.Thread(target=self._listen, daemon=True).start()

        self.game_window = Window(self)

        self.socket_info = None

        while not pr.window_should_close():
            self.game_window.step(self.socket_info)

        pr.close_window()
        self.send({"close_window": 1})

    def send(self, data):
        try:
            data["random_number"] = str(random.random())
            self.socket.send((json.dumps(data) + '\n').encode())
        except:
            pass

    def _listen(self):
        buffer = ""
        while True:
            try:
                data = self.socket.recv(1024).decode()
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        game_data = json.loads(line)
                        self.socket_info = game_data
                        print(self.socket_info)
            except:
                break


if __name__ == "__main__":
    GameUI()
