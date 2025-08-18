import pyray as pr
from ui_menu_files.main_sections.sprite_manager import *
from pynput.mouse import Controller

from ui_menu_files.main_sections.shop_section import ShopSection
from ui_menu_files.main_sections.biome_section import BiomeSection
from ui_menu_files.main_sections.settings_section import SettingSection

from useful_draw_functions import *

import math


class UI:
    def __init__(self, w, extra_w, h, font, main):
        self.w = w
        self.extra_w = extra_w

        self.h = h

        self.main = main

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

        # 4 sections, header, main, buttons, close button
        self.header_height = h // 6
        self.main_width = w // 1.25

        # general info
        self.border_thickness = w // 300
        self.screen_shake = 0
        self.error_shake = 0
        self.success_shake = 0

        self.minimize_window_hover = 0

        self.font = font

        # icons + section
        self.icons = {
            "shop": [load_sprite("content/ui/spr_shop_icon.png"), 0, 0, ORANGE, "Character Shop"],  # texture, hover scale, chosen, bg color, section name
            "environment": [load_sprite("content/ui/spr_environment_icon.png"), 0, 0, SOFT_GREEN, "Biomes"],
            "home": [load_sprite("content/ui/spr_home_icon.png"), 0, 0, LIGHT_BLUE, "Home"],
            "settings": [load_sprite("content/ui/spr_gear_icon.png"), 0, 0, PURPLE, "Settings"],
            "exit": [load_sprite("content/ui/spr_exit_icon.png"), 0, 0, SOFT_RED, "Exit"]
        }
        self.icon_order = ["shop", "environment", "home", "settings", "exit"]
        self.chosen_main_section = 1

        self.shop_section = ShopSection(self.border_thickness, self.main_width, h, self.p, self)
        self.biome_section = BiomeSection(self.border_thickness, self.main_width, h, self.p, self)
        self.settings_section = SettingSection(self.border_thickness, self.main_width, h, self.p, self)

        self.render_texture = None

        self.bg_color = SOFT_BROWN

    def step(self):
        self.window_location = pr.get_window_position()  # get location again, as the window might have moved

        if self.show:
            self.show_scale = min(self.show_scale + 1 / 10, 1)
        else:
            self.show_scale = max(self.show_scale - 1 / 10, 0)

        p = self.p
        render_texture = None

        self.w += self.extra_w

        # pop up when opening / closing shop
        if 1 > self.show_scale > 0:
            pr.rl_push_matrix()
            pr.rl_translatef(self.w / 2, self.h / 2, 0)
            pr.rl_rotatef(45 * (1 - self.show_scale), 0, 0, 1)
            pr.rl_scalef(self.show_scale, self.show_scale, 1)
            pr.rl_translatef(-self.w / 2, -self.h / 2, 0)

        # error shake
        if 1 >= self.error_shake > 0 >= self.success_shake:
            pr.rl_push_matrix()
            pr.rl_translatef(math.sin(self.error_shake * math.pi * 2) * self.w // 100, 0, 0)

            if self.render_texture:
                pr.unload_render_texture(self.render_texture)

            self.render_texture = pr.load_render_texture(self.w, self.h)
            pr.begin_texture_mode(self.render_texture)

        # success shake
        if 1 >= self.success_shake > 0:
            val = 4 * self.success_shake * (1 - self.success_shake) / 50

            pr.rl_push_matrix()
            pr.rl_translatef(self.w / 2, self.h / 2, 0)
            pr.rl_scalef(self.show_scale * (1 + val), self.show_scale * (1 + val), 1)
            pr.rl_translatef(-self.w / 2, -self.h / 2, 0)

            if self.render_texture:
                pr.unload_render_texture(self.render_texture)

            self.render_texture = pr.load_render_texture(self.w, self.h)
            pr.begin_texture_mode(self.render_texture)

        self.w -= self.extra_w

        if self.show_scale > 0:
            # screen shake when pressing a button icon
            if self.screen_shake > 0:
                pr.rl_push_matrix()
                pr.rl_translatef(self.w / 2, self.h / 2, 0)
                pr.rl_rotatef(math.sin(math.pi * 2 * self.screen_shake) * 0.5, 0, 0, 1)
                pr.rl_translatef(-self.w / 2, -self.h / 2, 0)

            # main ui sections
            self.button_section(self.main_width + p // 2, p, (self.w - self.main_width - p * 2) // 1.5, self.h - p * 2)
            self.header_section(p, p, self.main_width - p * 2, self.header_height)
            self.main_section(p, self.header_height + p, self.main_width - p * 2, self.h - self.header_height - p * 2)
            self.exit_section(self.main_width + p // 2 + (self.w - self.main_width - p * 2) // 1.5 + p * 3, p, self.extra_w, self.h - p * 2)

            if self.screen_shake > 0:
                self.screen_shake -= 1 / 20

                pr.rl_pop_matrix()

        if 1 > self.show_scale > 0:
            pr.rl_pop_matrix()

        if 1 >= self.error_shake > 0 >= self.success_shake:
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
            if self.success_shake <= 0:
                if self.render_texture:
                    pr.unload_render_texture(self.render_texture)
                    self.render_texture = None

        if 1 >= self.success_shake > 0:
            self.success_shake -= 1 / 10
            pr.rl_pop_matrix()
            pr.end_texture_mode()

            try:
                if self.success_shake > 0.5:
                    green = int(50 * (0.5 - (self.success_shake - 0.5)) * 2)
                else:
                    green = 50 - int(50 * (0.5 - self.success_shake) * 2)

                red_tint = pr.Color(min(255 - green, 255), 255, min(255 - green, 255), 255)
                pr.draw_texture_rec(self.render_texture.texture,
                                    pr.Rectangle(0, 0, self.render_texture.texture.width, -self.render_texture.texture.height),
                                    pr.Vector2(0, 0), red_tint)
            except:
                pass

    def header_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h + self.p * 6)
        pr.draw_rectangle_rounded(bg, 0.3, -1, self.bg_color)

        bg = pr.Rectangle(x, y, w, h + (self.h - self.header_height - self.p * 2))
        pr.draw_rectangle_rounded_lines_ex(bg, 0.09, -1, self.border_thickness, BLACK)

        # section title
        p = self.p * 2

        xx = x + p * 2
        ww = w * 0.6

        yy = y + p + self.p // 2
        hh = h - p * 2

        bg_col = self.icons[self.icon_order[self.chosen_main_section]][3]
        text = self.icons[self.icon_order[self.chosen_main_section]][4]

        bg = pr.Rectangle(xx, yy, ww, hh)
        pr.draw_rectangle_rounded(bg, 0.3, -1, bg_col)
        pr.draw_rectangle_rounded_lines_ex(bg, 0.35, -1, self.border_thickness, BLACK)

        font_size = int(pr.measure_text_ex(self.font, text, hh // 1.5, 0).y)
        draw_fitted_text(self.font, text, xx + ww // 2, yy + hh // 2, ww // 1.5, font_size, BLACK, align="center", center_y=True)

        # section currency
        xx = x + ww + p * 2 * 2
        ww = w - ww - p * 2 * 3

        bg = pr.Rectangle(xx, yy, ww, hh)
        pr.draw_rectangle_rounded(bg, 0.3, -1, WHITE)
        pr.draw_rectangle_rounded_lines_ex(bg, 0.35, -1, self.border_thickness, BLACK)

        text = f"Lv. {self.general_info['level']}"
        if self.chosen_main_section == 0:
            text = f'${self.general_info["currency"]}'

        draw_fitted_text(self.font, text, xx + ww // 2, yy + hh // 2, ww // 1.25, font_size, BLACK, align="center", center_y=True)

        #self.draw_text(f'${self.general_info["currency"]}', x + w // 2, y + (h - font_size) // 2, font_size, BLACK, text_align="center")

    def main_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        pr.draw_rectangle_rounded(bg, 0.1, -1, self.bg_color)
        #pr.draw_rectangle_rounded_lines_ex(bg, 0.1, -1, self.border_thickness, BLACK)

        # sections
        mouse_pos = self.get_mouse_pos()
        if self.chosen_main_section == 0:
            self.shop_section.step(x, y, (w + self.p) * self.show_scale, h * self.show_scale, mouse_pos)
        if self.chosen_main_section == 1:
            self.biome_section.step(x, y, w * self.show_scale, h * self.show_scale, mouse_pos)
        if self.chosen_main_section == 3:
            self.settings_section.step(x, y, w, h, mouse_pos)
        if self.chosen_main_section == 4:
            self.main.send({"close_window": 1})
            pr.close_window()

    def button_section(self, x, y, w, h):
        bg = pr.Rectangle(x, y, w, h)
        #pr.draw_rectangle_rounded(bg, 0.2, -1, WHITE)
        #pr.draw_rectangle_rounded_lines_ex(bg, 0.2, -1, self.border_thickness, BLACK)

        mouse_pos = self.get_mouse_pos()

        buttons = len(self.icon_order)

        # buttons
        for ind in range(buttons):
            h1 = int(h / buttons * ind)
            h2 = int(h / buttons * (ind+1))

            p = (w - (h2 - h1)) // 2

            hh = (h2 - h1) + p

            current_icon = self.icons[self.icon_order[ind]][0]
            hover_scale = self.icons[self.icon_order[ind]][1]
            chosen_scale = self.icons[self.icon_order[ind]][2]

            bg_col = self.icons[self.icon_order[ind]][3]

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

            # draw connecting background between chosen icon and main section
            if ind == self.chosen_main_section:
                left = self.p * 1.5 - self.border_thickness + self.p * 4

                # connecting white part
                bg = pr.Rectangle(x - left, h1 - int(p * 0.5) + self.border_thickness // 2, w + self.p * 1.5 + left, hh - (p * 1) + self.border_thickness // 2)
                pr.draw_rectangle_rounded(bg, 0.2, -1, self.bg_color)

                left += self.p * 4

                # black outline
                bg = pr.Rectangle(x - left, h1 - int(p * 0.5) + int(self.border_thickness * 0.75), w + self.p * 1.5 + left, hh - (p * 1))
                pr.draw_rectangle_rounded_lines_ex(bg, 0.25, -1, self.border_thickness, BLACK)

            # draw icon background
            bg = pr.Rectangle(x, h1 - int(p * 1.5), w, hh + p)
            pr.draw_rectangle_rounded(bg, 0.2, -1, bg_col)
            pr.draw_rectangle_rounded_lines_ex(bg, 0.2, -1, self.border_thickness, BLACK)

            # draw icon
            attributed_scale = max(hover_scale, chosen_scale)

            scale = w / current_icon.width / 1.25 * (attributed_scale / 6 + 1) / 1.4
            draw_sprite(current_icon, x + w // 2, y + h1 + (h2 - h1) // 2, scale,
                        origin="middle_center", tint=blend_colors(blend_colors(BLACK, BLACK, attributed_scale), WHITE, chosen_scale),
                        rot=math.sin(math.pi * 2 * attributed_scale) * 3)

    def exit_section(self, x, y, w, h):
        mouse_pos = self.get_mouse_pos()

        xx = x
        ww = w

        yy = y
        hh = w

        bg = pr.Rectangle(xx, yy, ww, hh)
        pr.draw_rectangle_rounded(bg, 0.25, -1, SOFT_RED)
        pr.draw_rectangle_rounded_lines_ex(bg, 0.3, -1, self.border_thickness, BLACK)

        if pr.check_collision_point_rec(mouse_pos, bg):
            self.minimize_window_hover = min(self.minimize_window_hover + 1 / 10, 1)

            if pr.is_mouse_button_pressed(pr.MouseButton(0)) and self.show and self.show_scale >= 1:
                self.main.send({"minimize_ui": True})
        else:
            self.minimize_window_hover = max(self.minimize_window_hover - 1 / 10, 0)

        # x icon
        p = self.border_thickness * 4
        ch = self.minimize_window_hover * (hh - p * 2)

        pr.draw_line_ex(pr.Vector2(xx + p, yy + hh - p - ch), pr.Vector2(xx + ww - p, yy + p + ch), p // 2, BLACK)
        pr.draw_line_ex(pr.Vector2(xx + p, yy + p + ch), pr.Vector2(xx + ww - p, yy + hh - p - ch), p // 2, BLACK)

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

    def draw_fitted_text(self, text, x, y, max_width, initial_size, color, align_right=False, align_center=False, center_y=False):
        size = initial_size
        text_metrics = pr.measure_text_ex(self.font, text, size, 0)
        text_width = text_metrics.x

        while text_width > max_width and size > 1:
            size -= 1
            text_metrics = pr.measure_text_ex(self.font, text, size, 0)
            text_width = text_metrics.x

        if align_right:
            x -= text_width

        if align_center:
            x -= text_width // 2

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

    def update_info(self, key, value):
        self.general_info[key] = value
        self.shop_section.general_info = self.general_info

    def get_info(self):
        # get main info
        return {
            self.general_info,

            self.mouse.position,

            self.shop_section,
            self.settings_section,
            self.biome_section
        }
