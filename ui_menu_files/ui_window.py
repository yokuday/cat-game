from screeninfo import get_monitors
import pyray as pr

import sys
import winxpgui

from hide_window import *
from ui_shop import UI


class Window:
    def __init__(self, main):
        monitors = get_monitors()
        primary = next((m for m in monitors if m.is_primary), monitors[0])

        self.max_width = primary.width
        self.max_height = primary.height

        self.height = int(self.max_height // 1.75)
        self.width = self.height

        self.main = main

        self.y_offset = 0

        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_TRANSPARENT | pr.ConfigFlags.FLAG_WINDOW_UNDECORATED | pr.ConfigFlags.FLAG_WINDOW_TOPMOST | pr.ConfigFlags.FLAG_VSYNC_HINT)
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

        #self.top_most = enforce_topmost(hwnd)

        self.show_window = False
        self.socket_info = {}

        self.font = pr.load_font_ex("content/Roboto-Medium.ttf", 96, None, 0)
        pr.set_texture_filter(self.font.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.ui = UI(self.width, self.height, self.font, self.main)

    def step(self, socket_info):
        if socket_info != self.socket_info:
            self.socket_info = socket_info

            if self.socket_info is not None:
                if self.socket_info.get("show_window", -1) == 1:
                    self.show_window = True
                if self.socket_info.get("show_window", -1) == 0:
                    self.show_window = False

                if self.socket_info.get("close_window", -1) == 1:
                    pr.close_window()
                    sys.exit()

                if self.socket_info.get("current_level", None):
                    self.ui.update_info("level", int(self.socket_info.get("current_level", 0)))

                if self.socket_info.get("current_biome", None):
                    self.ui.biome_section.current_biome = self.socket_info.get("current_biome", "forest")

                if self.socket_info.get("currency", None):
                    self.ui.update_info("currency", int(self.socket_info.get("currency", 0)))

                if self.socket_info.get("sold", None):
                    self.ui.convert_item(self.socket_info.get("sold", None))

        self.ui.show = self.show_window

        pr.begin_drawing()
        pr.clear_background(pr.Color(1, 3, 2, 0))

        self.ui.step()

        pr.end_drawing()
