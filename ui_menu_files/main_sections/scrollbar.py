import pyray as pr
from useful_draw_functions import *


class Scrollbar:
    def __init__(self, w, border_thickness, row_count):
        self.border_thickness = border_thickness
        self.row_count = row_count

        self.scroll_bar_width = w // 30
        self.scroll_bar_height = 0.2
        self.scroll = 0  # 0 to 1
        self.scroll_previous = self.scroll

        self.scroll_hover = 0  # check hover

        self.scroll_hold = 0
        self.scroll_clicked_inside_wheel = False
        self.mouse_previous_y = 0

    def scroll_bar(self, x, y, w, h, p, mouse_pos):
        scroll_width = self.scroll_bar_width
        scroll_height = h * 0.95

        scroll_x = x + w - scroll_width
        scroll_bar_y = y + h // 2 - scroll_height // 2

        # scroll bar background
        background_rec = pr.Rectangle(scroll_x, scroll_bar_y, scroll_width, scroll_height)
        pr.draw_rectangle_rounded(background_rec, 0.5, -1, LIGHT_GRAY)
        pr.draw_rectangle_rounded_lines_ex(background_rec, 0.75, -1, self.border_thickness, BLACK)

        # actual scroll bar
        scroll_height_max = scroll_height

        # change scroll_y based on, well, scroll
        scroll_y = scroll_bar_y + self.get_scroll_value() * scroll_height

        scroll_height = scroll_height * self.scroll_bar_height
        rec = pr.Rectangle(scroll_x, scroll_y, scroll_width, scroll_height)
        pr.draw_rectangle_rounded(rec, 0.5, -1, blend_colors(DARK_GRAY, DARKER_YELLOW, self.scroll_hover))
        pr.draw_rectangle_rounded_lines_ex(rec, 0.75, -1, self.border_thickness, BLACK)

        # check hover
        if pr.check_collision_point_rec(mouse_pos, rec) or self.scroll_hold:
            self.scroll_hover = min(self.scroll_hover + 1 / 5, 1)
        else:
            self.scroll_hover = max(self.scroll_hover - 1 / 5, 0)

        # check click / drag
        if not self.scroll_hold:
            if pr.is_mouse_button_pressed(pr.MouseButton(0)):
                if pr.check_collision_point_rec(mouse_pos, background_rec):
                    self.scroll_hold = 1

                    if pr.check_collision_point_rec(mouse_pos, rec):
                        self.scroll_clicked_inside_wheel = True
                        self.scroll_previous = min(max(self.scroll, self.scroll_bar_height / 2), 1-self.scroll_bar_height / 2)
                        self.mouse_previous_y = mouse_pos[1]
                    else:
                        self.scroll = max(min((mouse_pos[1] - scroll_bar_y) / scroll_height_max, 1), 0)
                        self.scroll_clicked_inside_wheel = False
        else:
            if not self.scroll_clicked_inside_wheel:
                self.scroll = max(min((mouse_pos[1] - scroll_bar_y) / scroll_height_max, 1), 0)
            else:
                scroll_previous = max(min((self.mouse_previous_y - scroll_bar_y) / scroll_height_max, 1), 0)
                scroll_next = max(min((mouse_pos[1] - scroll_bar_y) / scroll_height_max, 1), 0)

                self.scroll = max(min(self.scroll_previous + (scroll_next - scroll_previous), 1), 0)

            if pr.is_mouse_button_released(pr.MouseButton(0)):
                self.scroll_hold = 0

        # device scrolling + touchpad
        scroll_value = pr.get_mouse_wheel_move() / 3 / self.row_count

        if not self.scroll_hold:
            self.scroll = max(min(self.scroll - scroll_value, 1), 0)

    def get_scroll_value(self):
        return min(max(self.scroll - self.scroll_bar_height / 2, 0), 1 - self.scroll_bar_height)
