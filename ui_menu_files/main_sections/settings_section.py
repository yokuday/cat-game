import pyray as pr

from ui_menu_files.main_sections.sprite_manager import draw_sprite
from useful_draw_functions import *


class SettingSection:
    def __init__(self, border_thickness, w, h, p, ui):
        self.border_thickness = border_thickness
        self.w = w
        self.h = h

        self.p = p
        self.ui = ui

        self.font = ui.font

        self.options = [
            ["switch", "environment effects", True, 1, "environment_effects"],
            ["switch", "menu effects", True, 1, "menu_effects"]
        ]  # type, title, default, scale, key [ for changing effects ],

        self.s_h = int(h // 6)
        self.s_w = int(w // 1.2)

    def step(self, x, y, w, h, mouse_pos):
        yy = y + self.p
        for i, option in enumerate(self.options):
            if option[2]:
                self.options[i][3] = min(self.options[i][3] + 1 / 6, 1)
            else:
                self.options[i][3] = max(self.options[i][3] - 1 / 6, 0)

            if option[0] == "switch":
                self.switch(int(x + (w - self.s_w) // 2), int(yy), self.s_w, self.s_h, i, mouse_pos)

            yy += self.s_h

    def switch(self, x, y, w, h, option, mouse_pos):
        #pr.draw_rectangle(x, y, w, h, BLACK)

        sc = self.options[option][3]
        text = self.options[option][1]

        # switch background
        ww = w // 5
        hh = h // 3

        xx = x + ww // 5
        yy = y + h // 2 - hh // 2

        rec = pr.Rectangle(xx, yy, ww, hh)

        bob_outline = False

        # check for switch change
        if pr.check_collision_point_rec(mouse_pos, rec):
            bob_outline = True
            if pr.is_mouse_button_pressed(pr.MouseButton(0)):
                self.options[option][2] = not self.options[option][2]

        col = blend_colors(SOFT_RED, SOFT_GREEN, sc)

        pr.draw_rectangle_rounded(rec, 0.75, -1, col)
        pr.draw_rectangle_rounded_lines_ex(rec, 0.85, -1, hh // 15, BLACK)

        # switch bobble
        r = int(hh // 1.2 // 2)
        diff = int(hh - (r * 2))

        if bob_outline:
            pr.draw_circle(int(xx + r + diff + (sc * (ww - r * 2 - diff * 2))), y + h // 2, int(r * 1.1), BLACK)
        pr.draw_circle(int(xx + r + diff + (sc * (ww - r * 2 - diff * 2))), y + h // 2, r, WHITE)

        # text
        draw_fitted_text(self.font, text, x + int(ww * 1.5), y + h // 2,
                         initial_size=50, color=BLACK, max_width=(w - ww) // 1.2, max_height=hh // 1.25, center_y=True)
