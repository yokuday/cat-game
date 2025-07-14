import pyray as pr
import math


class MainUI:
    def __init__(self, w, h, player_info):
        self.w = w
        self.h = h

        width = self.w // 6
        self.exp_bar_size = [width, min(self.h // 12, width // 3)]
        self.exp_bar_padding = self.h // 25

        self.exp_bar_rectangle = pr.Rectangle(self.exp_bar_padding, self.h - self.exp_bar_padding - self.exp_bar_size[1],
                                    self.exp_bar_size[0], self.exp_bar_size[1])
        self.exp_variable_pi = 0
        self.exp_prev = player_info.info["current_exp"]

        self.info = player_info.info
        self.font = pr.Font()

    # what's shown in the simulation environment
    def field(self):
        self.exp_bar()

    def exp_bar(self):
        white = pr.Color(255, 255, 255, 255)
        black = pr.Color(0, 0, 0, 255)
        yellow = pr.Color(220, 229, 94, 255)

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
        center_y = self.h - self.exp_bar_padding - self.exp_bar_size[1] / 2

        pr.rl_push_matrix()
        pr.rl_translatef(center_x, center_y, 0)
        pr.rl_rotatef(rot, 0, 0, 1)
        pr.rl_translatef(-center_x, -center_y, 0)

        pr.draw_rectangle_rounded(self.exp_bar_rectangle, 0.5, -1, white)

        # exp bar progress
        exp_bar_rectangle = pr.Rectangle(self.exp_bar_padding, self.h - self.exp_bar_padding - self.exp_bar_size[1],
                                         self.exp_bar_size[0] * (exp / required_exp), self.exp_bar_size[1])
        pr.draw_rectangle_rounded(exp_bar_rectangle, 0.5, -1, yellow)

        # exp bar outline
        pr.draw_rectangle_rounded_lines_ex(self.exp_bar_rectangle, 0.5, -1, self.exp_bar_padding / 4, black)

        # draw level text
        pos = pr.Vector2(self.exp_bar_padding * 2, self.h - self.exp_bar_padding - self.exp_bar_size[1])
        origin = pr.Vector2(0, 0)
        pr.draw_text_pro(self.font, f"Lv. {self.info['current_level']}",
                         pos, origin, 0, self.exp_bar_size[1], 0, black)

        # draw exp text
        exp_text = f"{exp} / {required_exp}"
        text_size = pr.measure_text(exp_text, self.exp_bar_size[1])
        origin = pr.Vector2(0, 0)  # text has to go from right to left
        pos = pr.Vector2(self.exp_bar_padding + self.exp_bar_size[0] - text_size,
                         self.h - self.exp_bar_padding - self.exp_bar_size[1])
        pr.draw_text_pro(self.font, exp_text, pos, origin, 0, self.exp_bar_size[1], 0, black)

        pr.rl_pop_matrix()

    def menu(self):
        pass
