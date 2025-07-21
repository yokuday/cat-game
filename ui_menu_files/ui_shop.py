import pyray as pr
from sprite_manager import *
from pynput.mouse import Controller

from main_sections.shop_section import ShopSection

from useful_draw_functions import *

import math


class UI:
    def __init__(self, w, h, font):
        self.w = w
        self.h = h

        self.p = 10

        # mouse input
        self.mouse = Controller()
        self.window_location = pr.get_window_position()

        # ui general info
        self.show = False
        self.show_scale = 0

        self.general_info = {
            "currency": 0,
            "level": 0
        }

        # 3 sections, header, main, buttons
        self.header_height = h // 10
        self.main_width = w // 1.25

        # general info
        self.border_thickness = w // 200
        self.screen_shake = 0
        self.error_shake = 0

        self.font = font

        # icons + section
        self.icons = {
            "shop": [load_sprite("content/ui/spr_shop_icon.png"), 0, 0],  # texture, hover scale, chosen
            "npc_manager": [load_sprite("content/ui/spr_npcs_icon.png"), 0, 0],
            "environment": [load_sprite("content/ui/spr_environment_icon.png"), 0, 0],
            "home": [load_sprite("content/ui/spr_home_icon.png"), 0, 0]
        }
        self.icon_order = ["shop", "npc_manager", "environment", "home"]
        self.chosen_main_section = 0

        self.shop_section = ShopSection(self.border_thickness, self.main_width, h, self.p, self)

        self.render_texture = None

    def step(self):
        if not self.show:
            self.show_scale = min(self.show_scale + 1 / 10, 1)
        else:
            self.show_scale = max(self.show_scale - 1 / 10, 0)

        p = self.p
        render_texture = None

        # pop up when opening / closing shop
        if 1 > self.show_scale > 0:
            pr.rl_push_matrix()
            pr.rl_translatef(self.w / 2, self.h / 2, 0)
            pr.rl_rotatef(45 * (1 - self.show_scale), 0, 0, 1)
            pr.rl_scalef(self.show_scale, self.show_scale, 1)
            pr.rl_translatef(-self.w / 2, -self.h / 2, 0)

        # error shake
        if 1 >= self.error_shake > 0:
            pr.rl_push_matrix()
            pr.rl_translatef(math.sin(self.error_shake * math.pi * 2) * self.w // 100, 0, 0)

            if self.render_texture:
                pr.unload_render_texture(self.render_texture)

            self.render_texture = pr.load_render_texture(self.w, self.h)
            pr.begin_texture_mode(self.render_texture)

        if self.show_scale > 0:
            # screen shake when pressing a button icon
            if self.screen_shake > 0:
                pr.rl_push_matrix()
                pr.rl_translatef(self.w / 2, self.h / 2, 0)
                pr.rl_rotatef(math.sin(math.pi * 2 * self.screen_shake) * 0.5, 0, 0, 1)
                pr.rl_translatef(-self.w / 2, -self.h / 2, 0)

            # main ui sections
            self.header_section(p, p, self.w - p * 2, self.header_height - p * 2)
            self.main_section(p, self.header_height + p, self.main_width - p * 2, self.h - self.header_height - p * 2)
            self.button_section(self.main_width + p, self.header_height + p, self.w - self.main_width - p*2, self.h - self.header_height - p*2)

            if self.screen_shake > 0:
                self.screen_shake -= 1 / 20

                pr.rl_pop_matrix()

        if 1 > self.show_scale > 0:
            pr.rl_pop_matrix()

        if 1 >= self.error_shake > 0:
            self.error_shake -= 1 / 15
            pr.rl_pop_matrix()
            pr.end_texture_mode()

            try:
                if self.error_shake > 0.5:
                    red = int(50 * (0.5 - (self.error_shake - 0.5)) * 2)
                else:
                    red = 50 - int(50 * (0.5 - self.error_shake) * 2)

                red_tint = pr.Color(255, min(255 - red, 255), min(255 - red, 255), 255)
                pr.draw_texture_rec(self.render_texture.texture,
                                    pr.Rectangle(0, 0, self.render_texture.texture.width, -self.render_texture.texture.height),
                                    pr.Vector2(0, 0), red_tint)
            except:
                pass
        else:
            if self.render_texture:
                pr.unload_render_texture(self.render_texture)
                self.render_texture = None

    def header_section(self, x, y, w, h):
        p = w // 4
        bg = pr.Rectangle(x + p, y, w - p * 2, h)
        pr.draw_rectangle_rounded(bg, 0.3, -1, WHITE)
        pr.draw_rectangle_rounded_lines_ex(bg, 0.3, -1, self.border_thickness, BLACK)

        font_size = int(h // 1.2)

        self.draw_text(f'${self.general_info["currency"]}', x + w // 2, y + (h - font_size) // 2, font_size, BLACK, text_align="center")

    def main_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        pr.draw_rectangle_rounded(bg, 0.1, -1, WHITE)
        pr.draw_rectangle_rounded_lines_ex(bg, 0.1, -1, self.border_thickness, BLACK)

        # sections
        mouse_pos = self.get_mouse_pos()
        if self.chosen_main_section == 0:
            self.shop_section.step(x, y, w * self.show_scale, h * self.show_scale, mouse_pos)

    def button_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        pr.draw_rectangle_rounded(bg, 0.2, -1, WHITE)
        pr.draw_rectangle_rounded_lines_ex(bg, 0.2, -1, self.border_thickness, BLACK)

        mouse_pos = self.get_mouse_pos()

        buttons = len(self.icon_order)

        # buttons
        for ind in range(buttons):
            h1 = int(h / buttons * ind)
            h2 = int(h / buttons * (ind+1))

            current_icon = self.icons[self.icon_order[ind]][0]
            hover_scale = self.icons[self.icon_order[ind]][1]
            chosen_scale = self.icons[self.icon_order[ind]][2]

            # check for button hover + click
            rec = pr.Rectangle(x, y + h1, w, h2 - h1)
            if pr.check_collision_point_rec(mouse_pos, rec):
                self.icons[self.icon_order[ind]][1] = min(hover_scale + 1 / 10, 1)

                if pr.is_mouse_button_pressed(pr.MouseButton(0)) and ind != self.chosen_main_section:
                    self.screen_shake = 1
                    self.chosen_main_section = ind
                    self.icons[self.icon_order[ind]][2] = hover_scale

            else:
                self.icons[self.icon_order[ind]][1] = max(hover_scale - 1 / 10, 0)

            # chosen scale
            if self.chosen_main_section == ind:
                self.icons[self.icon_order[ind]][2] = min(chosen_scale + 1 / 10, 1)
            else:
                self.icons[self.icon_order[ind]][2] = max(chosen_scale - 1 / 10, 0)

            # draw icon
            attributed_scale = max(hover_scale, chosen_scale)

            scale = w // current_icon.width / 1.25 * (attributed_scale / 6 + 1)
            draw_sprite(current_icon, x + w // 2, y + h1 + (h2 - h1) // 2, scale,
                        origin="middle_center", tint=blend_colors(blend_colors(BLACK, DARKER_YELLOW, attributed_scale), ORANGE, chosen_scale),
                        rot=math.sin(math.pi * 2 * attributed_scale) * 3)

    def draw_text(self, text, pos_x, pos_y, font_size, color, text_align="left", outline_size=0, outline_color=BLACK):
        text = f"{text}"

        text_width = int(pr.measure_text_ex(self.font, text, font_size, 0).x)
        centered_x = pos_x

        if text_align == "center":
            centered_x = pos_x - text_width // 2

        if outline_size != 0:
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
            self.update_info("currency", self.general_info["currency"] + 1)

    def get_mouse_pos(self):
        pos = self.mouse.position

        if self.show_scale >= 1:
            return [pos[0] - self.window_location.x, pos[1] - self.window_location.y]
        return [-1, -1]

    def stub(self):
        pass

    def update_info(self, key, value):
        self.general_info[key] = value
        self.shop_section.general_info = self.general_info
