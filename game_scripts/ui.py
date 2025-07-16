import pyray as pr
from pynput.mouse import Button, Controller

import math

white = pr.Color(255, 255, 255, 255)
black = pr.Color(0, 0, 0, 255)
yellow = pr.Color(220, 229, 94, 255)


def blend_colors(color1: pr.Color, color2: pr.Color, t: float) -> pr.Color:
    clamp = lambda x: max(0.0, min(1.0, x))  # Ensure t stays between 0 and 1
    t = clamp(t)

    r = int(color1.r + (color2.r - color1.r) * t)
    g = int(color1.g + (color2.g - color1.g) * t)
    b = int(color1.b + (color2.b - color1.b) * t)
    a = int(color1.a + (color2.a - color1.a) * t)

    return pr.Color(r, g, b, a)


class MainUI:
    def __init__(self, w, h, player_info, ui_window):
        self.w = w
        self.h = h
        self.y_offset = 0

        self.ui_window = ui_window

        self.info = player_info.info
        self.font = pr.Font()

        self.mouse = Controller()

        self.window_location = pr.get_window_position()

        # EXP BAR
        width = self.w // 6
        self.exp_bar_size = [width, min(self.h // 12, width // 3)]
        self.exp_bar_padding = self.h // 25

        self.exp_bar_rectangle = pr.Rectangle(self.exp_bar_padding, self.h - self.exp_bar_padding - self.exp_bar_size[1] + self.y_offset,
                                    self.exp_bar_size[0], self.exp_bar_size[1])
        self.exp_variable_pi = 0
        self.exp_prev = player_info.info["current_exp"]

        # ICONS
        self.arrow_padding = self.exp_bar_padding
        self.arrow_size = [self.arrow_padding * 3, self.arrow_padding * 3]
        self.arrow_hover = 0

        self.arrow_clicked = False

    # what's shown in the simulation environment
    def field(self):
        self.exp_bar()
        self.icons()

    def exp_bar(self):
        if self.exp_variable_pi > 0:
            self.exp_variable_pi += math.pi / 20
            if self.exp_variable_pi >= 2*math.pi:
                self.exp_variable_pi = 0

        if self.info["current_exp"] != self.exp_prev:
            self.exp_prev = self.info["current_exp"]
            if self.exp_variable_pi <= 0:
                self.exp_variable_pi += math.pi / 20

        rot = math.sin(self.exp_variable_pi)

        # exp bar background
        exp = self.info["current_exp"]
        required_exp = self.info["required_exp"]

        center_x = self.exp_bar_padding + self.exp_bar_size[0] / 2
        center_y = self.h - self.exp_bar_padding - self.exp_bar_size[1] / 2 + self.y_offset

        pr.rl_push_matrix()
        pr.rl_translatef(center_x, center_y, 0)
        pr.rl_rotatef(rot, 0, 0, 1)
        pr.rl_translatef(-center_x, -center_y, 0)

        pr.draw_rectangle_rounded(self.exp_bar_rectangle, 0.5, -1, white)

        # exp bar progress
        exp_bar_rectangle = pr.Rectangle(self.exp_bar_padding, self.h - self.exp_bar_padding - self.exp_bar_size[1] + self.y_offset,
                                         self.exp_bar_size[0] * (exp / required_exp), self.exp_bar_size[1])
        pr.draw_rectangle_rounded(exp_bar_rectangle, 0.5, -1, yellow)

        # exp bar outline
        pr.draw_rectangle_rounded_lines_ex(self.exp_bar_rectangle, 0.5, -1, self.exp_bar_padding / 4, black)

        # draw level text
        pos = pr.Vector2(self.exp_bar_padding * 2, self.h - self.exp_bar_padding - self.exp_bar_size[1] + self.y_offset)
        origin = pr.Vector2(0, 0)
        pr.draw_text_pro(self.font, f"Lv. {self.info['current_level']}",
                         pos, origin, 0, self.exp_bar_size[1], 0, black)

        # draw exp text
        exp_text = f"{exp} / {required_exp}"
        text_size = pr.measure_text(exp_text, self.exp_bar_size[1])
        origin = pr.Vector2(0, 0)  # text has to go from right to left, so pos is taking care of that
        pos = pr.Vector2(self.exp_bar_padding + self.exp_bar_size[0] - text_size,
                         self.h - self.exp_bar_padding - self.exp_bar_size[1] + self.y_offset)
        pr.draw_text_pro(self.font, exp_text, pos, origin, 0, self.exp_bar_size[1], 0, black)

        pr.rl_pop_matrix()

    def icons(self):
        # arrow icon
        x = self.w - self.arrow_padding * 3 - self.arrow_size[0]
        y = self.h - self.arrow_padding - self.arrow_size[1] + self.y_offset

        mouse = self.get_mouse_pos()

        # check for hover
        rectangle = pr.Rectangle(x, y, self.arrow_size[0], self.arrow_size[1])
        if pr.check_collision_point_rec(mouse, rectangle):
            self.arrow_hover = min(self.arrow_hover + 1 / 10, 1)

            if pr.is_mouse_button_pressed(pr.MouseButton(0)):
                self.arrow_clicked = not self.arrow_clicked

                self.ui_window.send({"show_window": self.arrow_clicked})
        else:
            self.arrow_hover = max(self.arrow_hover - 1 / 10, 0)

        w = self.arrow_size[0] * (1 + self.arrow_hover / 5)
        h = self.arrow_size[1] * (1 + self.arrow_hover / 5)

        x = self.w - self.arrow_padding * 3 - w
        y = self.h - self.arrow_padding - h + self.y_offset

        rectangle = pr.Rectangle(x, y, w, h)

        col = blend_colors(white, yellow, self.arrow_hover)

        pr.draw_rectangle_rounded(rectangle, 0.5, -1, col)
        pr.draw_rectangle_rounded_lines_ex(rectangle, 0.5, -1, self.arrow_padding / 4, black)

        end_pos = pr.Vector2(x + w / 2, y + h / 4)
        pr.draw_line_ex(pr.Vector2(x + w / 6, y + h / 1.3), end_pos, self.arrow_padding / 2, black)
        pr.draw_line_ex(pr.Vector2(x + w - w / 6, y + h / 1.3), end_pos, self.arrow_padding / 2, black)

    def get_mouse_pos(self):
        pos = self.mouse.position
        return [pos[0] - self.window_location.x, pos[1] - self.window_location.y]

    def menu(self):
        pass
