import pyray as pr


WHITE = pr.Color(255,255,255,255)
BLACK = pr.Color(0,0,0,255)
GREEN = pr.Color(0, 255, 0, 255)
RED = pr.Color(255,0,0,255)


class UI:
    def __init__(self, w, h, font):
        self.w = w
        self.h = h

        self.show = False
        self.show_scale = 0

        self.currency = 0  # how much coins

        # 3 sections, header, main, buttons
        self.header_height = h // 10
        self.main_width = w // 1.4

        self.font = font

    def step(self):
        if not self.show:
            self.show_scale = min(self.show_scale + 1 / 10, 1)
        else:
            self.show_scale = max(self.show_scale - 1 / 10, 0)

        if self.show_scale > 0:
            pr.rl_push_matrix()
            pr.rl_translatef(self.w / 2, self.h / 2, 0)
            pr.rl_rotatef(45 * (1 - self.show_scale), 0, 0, 1)
            pr.rl_scalef(self.show_scale, self.show_scale, 1)
            pr.rl_translatef(-self.w / 2, -self.h / 2, 0)

            self.header_section(0, 0, self.w, self.header_height)
            self.main_section(0, self.header_height, self.main_width, self.h - self.header_height)
            self.button_section(self.main_width, self.header_height, self.w - self.main_width, self.h - self.header_height)

            pr.rl_pop_matrix()

    def header_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        pr.draw_rectangle_rec(bg, WHITE)

        font_size = int(h // 1.2)

        self.draw_outlined_text(self.currency, x + w // 2, y + (h - font_size) // 2, font_size, WHITE, int(font_size // 30), BLACK)

    def main_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        #pr.draw_rectangle_rec(bg, BLACK)

    def button_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        #pr.draw_rectangle_rec(bg, GREEN)

        buttons = 4
        # buttons
        for ind in range(buttons):
            col = pr.Color(ind * 50, ind * 50, ind * 50, 255)
            h1 = int(h / buttons * ind)
            h2 = int(h / buttons * (ind+1))
            pr.draw_rectangle(int(x), int(y + h1), int(w), int(h2 - h1), col)

    def draw_outlined_text(self, text, pos_x, pos_y, font_size, color, outline_size, outline_color):
        text = f"{text}"

        text_width = int(pr.measure_text_ex(self.font, text, font_size, 0).x)
        centered_x = pos_x - text_width // 2

        pr.draw_text_ex(self.font, text, pr.Vector2(centered_x - outline_size, pos_y - outline_size), font_size, 0, outline_color)
        pr.draw_text_ex(self.font, text, pr.Vector2(centered_x + outline_size, pos_y - outline_size), font_size, 0, outline_color)
        pr.draw_text_ex(self.font, text, pr.Vector2(centered_x - outline_size, pos_y + outline_size), font_size, 0, outline_color)
        pr.draw_text_ex(self.font, text, pr.Vector2(centered_x + outline_size, pos_y + outline_size), font_size, 0, outline_color)

        pr.draw_text_ex(self.font, text, pr.Vector2(centered_x, pos_y), font_size, 0, color)

    def draw_fitted_text(self, text, x, y, max_width, initial_size, color, align_right=False, center_y=False):
        size = initial_size
        text_metrics = pr.measure_text_ex(self.font, text, size, 0)
        text_width = text_metrics.x

        while text_width > max_width and size > 1:
            size -= 1
            text_metrics = pr.measure_text_ex(self.font, text, size, 0)
            text_width = text_metrics.x

        if align_right:
            x -= text_width

        if center_y:
            y -= text_metrics.y / 2

        pr.draw_text_pro(self.font, text, pr.Vector2(x, y), pr.Vector2(0, 0), 0, size, 0, color)

    def convert_item(self, item):
        if item == "item_wood":
            self.currency += 1
