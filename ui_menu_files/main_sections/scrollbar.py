import pyray as pr
from useful_draw_functions import *
from ui_menu_files.main_sections.sprite_manager import draw_sprite, load_sprite


class Scrollbar:
    def __init__(self, w, border_thickness, row_count, coords, sprite):
        self.border_thickness = border_thickness
        self.row_count = row_count

        self.coords = coords

        self.scroll_bar_sprite = sprite

        self.scroll = 0  # 0 to 1
        self.scroll_previous = self.scroll

        self.scroll_hover = 0  # check hover

        self.scroll_hold = 0
        self.scroll_clicked_inside_wheel = False
        self.mouse_previous_y = 0

        x, w, y, h = get_coord_values(self.coords["scrollbar"])
        self.scroll_bar_scale = w / (self.scroll_bar_sprite.width / 3 / 20 * 5.9)
        self.scroll_bar_height = self.scroll_bar_sprite.height * self.scroll_bar_scale / h * 0.95

    def scroll_bar(self, mouse_pos):
        x, w, y, h = get_coord_values(self.coords["scrollbar"])

        # actual scroll bar
        scroll_height_max = h

        # change scroll_y based on, well, scroll
        scroll_y = y + self.get_scroll_value() * h

        scroll_height = h * self.scroll_bar_height

        rec = pr.Rectangle(x, scroll_y, w, scroll_height)
        draw_sprite(self.scroll_bar_sprite, x - self.scroll_bar_scale * 6, scroll_y + self.scroll_bar_scale * 2, self.scroll_bar_scale, frame_count=3, current_frame=2)

        # check hover
        if pr.check_collision_point_rec(mouse_pos, rec) or self.scroll_hold:
            self.scroll_hover = min(self.scroll_hover + 1 / 5, 1)
        else:
            self.scroll_hover = max(self.scroll_hover - 1 / 5, 0)

        # check click / drag
        if not self.scroll_hold:
            if pr.is_mouse_button_pressed(pr.MouseButton(0)):
                if pr.check_collision_point_rec(mouse_pos, pr.Rectangle(x, y, w, h)):
                    self.scroll_hold = 1

                    if pr.check_collision_point_rec(mouse_pos, rec):
                        self.scroll_clicked_inside_wheel = True
                        self.scroll_previous = min(max(self.scroll, self.scroll_bar_height / 2), 1-self.scroll_bar_height / 2)
                        self.mouse_previous_y = mouse_pos[1]
                    else:
                        self.scroll = max(min((mouse_pos[1] - y) / scroll_height_max, 1), 0)
                        self.scroll_clicked_inside_wheel = False
        else:
            if not self.scroll_clicked_inside_wheel:
                self.scroll = max(min((mouse_pos[1] - y) / scroll_height_max, 1), 0)
            else:
                scroll_previous = max(min((self.mouse_previous_y - y) / scroll_height_max, 1), 0)
                scroll_next = max(min((mouse_pos[1] - y) / scroll_height_max, 1), 0)

                self.scroll = max(min(self.scroll_previous + (scroll_next - scroll_previous), 1), 0)

            if pr.is_mouse_button_released(pr.MouseButton(0)):
                self.scroll_hold = 0

        # device scrolling + touchpad
        scroll_value = pr.get_mouse_wheel_move() / 3 / self.row_count

        if not self.scroll_hold:
            self.scroll = max(min(self.scroll - scroll_value, 1), 0)

    def get_scroll_value(self):
        return min(max(self.scroll - self.scroll_bar_height / 2, 0), 1 - self.scroll_bar_height)
