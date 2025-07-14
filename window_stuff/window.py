import pyray as pr
from draw_events.test_functions import Functions
from window_stuff.hide_window import *

from game_scripts import game
from game_scripts.player_scripts import player_info

from screeninfo import get_monitors

import win32api
import win32con
import win32gui
import winxpgui

import os, sys, json


def get_size(file="config.json"):
    try:
        with open(file, 'r') as f:
            return json.load(f).get('current_size', 2)
    except:
        return 2


def set_size(size, file="config.json"):
    data = {}
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except:
            pass

    data['current_size'] = size
    with open(file, 'w') as f:
        json.dump(data, f)


class Window:
    def __init__(self, above_taskbar=True):
        monitors = get_monitors()
        primary = next((m for m in monitors if m.is_primary), monitors[0])

        self.max_width = primary.width
        self.max_height = primary.height

        self.current_size = get_size()
        self.size_options = [20, 10, 7, 5, 4, 3, 2]

        self.width = self.max_width
        self.height = self.max_height // self.size_options[self.current_size]

        self.taskbar_height = get_taskbar_height()
        print(self.taskbar_height, self.max_height, self.max_width)

        if not above_taskbar:
            self.taskbar_height = 0

        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_TRANSPARENT | pr.ConfigFlags.FLAG_WINDOW_UNDECORATED | pr.ConfigFlags.FLAG_WINDOW_TOPMOST)
        pr.init_window(self.width, self.height, "Idle - game")
        pr.set_window_position(0, self.max_height - self.height - self.taskbar_height)

        pr.set_target_fps(60)

        # set window click through
        hwnd = win32gui.FindWindow(None, "Idle - game")
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(1, 3, 2), 255, win32con.LWA_COLORKEY)

        # hide window from taskbar
        hide_from_taskbar(hwnd)
        set_topmost(hwnd)

        self.top_most = enforce_topmost(hwnd)

        # TEST functions for draw events
        self.test_functions = Functions(self.width, self.height)

        # actual game logic
        self.player_info = player_info.PlayerInfo()
        self.game = game.Game(self.width, self.height, self.player_info)

    def main_step(self):
        pr.begin_drawing()
        pr.clear_background(pr.Color(1, 3, 2, 0))  # Fully transparent background

        # game step
        self.game.step()

        # ui
        self.game.game_ui()

        # key press
        char_pressed = pr.get_char_pressed()
        if char_pressed == 43 or char_pressed == 45:
            if char_pressed == 43:
                self.current_size = min(self.current_size + 1, len(self.size_options) - 1)
            else:
                self.current_size = max(self.current_size - 1, 0)
            set_size(self.current_size)

            self.height = self.max_height // self.size_options[self.current_size]

            pr.set_window_size(self.width, self.height)
            pr.set_window_position(0, self.max_height - self.height - self.taskbar_height)

            self.game = game.Game(self.width, self.height, self.player_info)

            #script_path = f"{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}/main.py"
            #os.execv(sys.executable, [sys.executable, script_path])
            #os.execv(sys.executable, [sys.executable])   this should work if game is an executable

        # fps
        self.test_functions.draw_fps()

        pr.end_drawing()

