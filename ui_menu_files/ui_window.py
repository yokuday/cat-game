from screeninfo import get_monitors
import pyray as pr

import sys
import winxpgui

from hide_window import *


class Window:
    def __init__(self):
        monitors = get_monitors()
        primary = next((m for m in monitors if m.is_primary), monitors[0])

        self.max_width = primary.width
        self.max_height = primary.height

        self.height = int(self.max_height // 2)
        self.width = self.height

        self.y_offset = 0

        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_TRANSPARENT | pr.ConfigFlags.FLAG_WINDOW_UNDECORATED | pr.ConfigFlags.FLAG_WINDOW_TOPMOST)
        pr.init_window(self.width, self.height, "Idle - game - ui_window")
        pr.set_window_position((self.max_width - self.width) // 2, (self.max_height - self.height) // 2)

        pr.set_target_fps(60)

        # set window click through
        hwnd = win32gui.FindWindow(None, "Idle - game - ui_window")
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(1, 3, 2), 255, win32con.LWA_COLORKEY)

        # hide window from taskbar
        hide_from_taskbar(hwnd)
        set_topmost(hwnd)

        self.top_most = enforce_topmost(hwnd)

        self.show_window = False
        self.socket_info = None

    def step(self, socket_info):
        if socket_info != self.socket_info:
            self.socket_info = socket_info

            if self.socket_info:
                if self.socket_info.get("show_window", -1) == 1:
                    self.show_window = True
                if self.socket_info.get("show_window", -1) == 0:
                    self.show_window = False

                if self.socket_info.get("close_window", -1) == 1:
                    pr.close_window()
                    sys.exit()

                self.socket_info = None

        pr.begin_drawing()

        if not self.show_window:
            pr.clear_background(pr.Color(1, 3, 2, 0))
        else:
            pr.clear_background(pr.Color(255, 255, 255, 255))

        pr.end_drawing()
