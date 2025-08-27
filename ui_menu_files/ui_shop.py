import pyray as pr
from ui_menu_files.main_sections.sprite_manager import *
from pynput.mouse import Controller

from ui_menu_files.main_sections.shop_section import ShopSection
from ui_menu_files.main_sections.biome_section import BiomeSection
from ui_menu_files.main_sections.settings_section import SettingSection

from useful_draw_functions import *

import math


class UI:
    def __init__(self, w, extra_w, h, font, main, primary_sprite):
        self.w = w
        self.extra_w = extra_w

        self.h = h

        self.main = main

        self.primary_ui = primary_sprite
        self.primary_ui_frames = 6

        sc = h / primary_sprite.height
        self.primary_ui_scale = sc

        self.coords = {
            "title": [[int(36 * sc), int(21 * sc)], [int(135 * sc), int(37 * sc)]],
            "currency": [[int(150 * sc), int(24 * sc)], [int(175 * sc), int(35 * sc)]],

            "buttons": [[[int(195 * sc), int(19 * sc)], [int(221 * sc), int(48 * sc)]], int(32 * sc), 6],  # +32 per button, 6 buttons
            "x_button": [[int(231 * sc), int(22 * sc)], [int(248 * sc), int(41 * sc)]],

            "scrollbar": [[int(180 * sc), int(43 * sc)], [int(186 * sc), int(205 * sc)]],
            "main_area": [[int(24 * sc), int(47 * sc)], [int(174 * sc), int(206 * sc)]]
        }

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
            "friends": [load_sprite("content/ui/spr_npcs_icon.png"), 0, 0, LIGHT_BLUE, "Characters"],
            "settings": [load_sprite("content/ui/spr_gear_icon.png"), 0, 0, PURPLE, "Settings"],
            "exit": [load_sprite("content/ui/spr_exit_icon.png"), 0, 0, SOFT_RED, "Exit"],
        }
        self.icon_order = ["shop", "environment", "home", "friends", "settings", "exit"]
        self.chosen_main_section = 0

        self.buttons = load_sprite("content/ui/elements/spr_tab_buttons.png")
        self.scroll_bar_sprite = load_sprite("content/ui/elements/spr_esc_scroll.png")

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

            # main background
            draw_sprite(self.primary_ui, 0, 0, self.primary_ui_scale, frame_count=6, current_frame=self.chosen_main_section)

            # main ui sections
            self.button_section()
            self.header_section()
            if self.show_scale >= 1:
                self.main_section()
            self.exit_section()

            #print(self.get_mouse_pos())
            #draw_sprite(self.ui_sketch, 0, 0, self.h / self.ui_sketch.height)

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

    def header_section(self):
        # section title
        x, w, y, h = get_coord_values(self.coords["title"])

        text = self.icons[self.icon_order[self.chosen_main_section]][4]

        font_size = int(pr.measure_text_ex(self.font, text, h // 1.5, 0).y)
        draw_fitted_text(self.font, text, x + w // 2, y + h // 2, w // 1.5, font_size, BLACK, align="center", center_y=True)

        # section currency
        x, w, y, h = get_coord_values(self.coords["currency"])

        text = str(self.general_info["currency"])
        if self.chosen_main_section == 1:
            text = f"Lv. {self.general_info['level']}"

        draw_fitted_text(self.font, text, x + w // 2, y + h // 2, w // 1.25, font_size, BLACK, align="center", center_y=True)

    def main_section(self):
        # bg = pr.Rectangle(x, y, w, h)
        # pr.draw_rectangle_rounded(bg, 0.1, -1, self.bg_color)
        #pr.draw_rectangle_rounded_lines_ex(bg, 0.1, -1, self.border_thickness, BLACK)

        # sections
        mouse_pos = self.get_mouse_pos()
        if self.chosen_main_section == 0:
            self.shop_section.step(mouse_pos)
        if self.chosen_main_section == 1:
            self.biome_section.step(mouse_pos)
        if self.chosen_main_section == 4:
            self.settings_section.step(mouse_pos)
        if self.chosen_main_section == 5:
            self.main.send({"close_window": 1})
            pr.close_window()

    def button_section(self):
        mouse_pos = self.get_mouse_pos()

        buttons = len(self.icon_order)

        x, w, y, h = get_coord_values(self.coords["buttons"])

        jump_y = self.coords["buttons"][1]

        # buttons
        for ind in range(buttons):
            hover_scale = self.icons[self.icon_order[ind]][1]
            chosen_scale = self.icons[self.icon_order[ind]][2]

            # check for button hover + click
            rec = pr.Rectangle(x, y + jump_y * ind, w, h)
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
            scale = h / self.buttons.height * 1.05
            draw_sprite(self.buttons, x - scale, y + jump_y * ind - scale * 2, scale, tint=WHITE, frame_count=buttons*2, current_frame=ind*2 + round(chosen_scale))

    def exit_section(self):
        mouse_pos = self.get_mouse_pos()

        x, w, y, h = get_coord_values(self.coords["x_button"])

        bg = pr.Rectangle(x, y, w, h)

        frame = 0
        if pr.check_collision_point_rec(mouse_pos, bg):
            self.minimize_window_hover = min(self.minimize_window_hover + 1 / 10, 1)

            if pr.is_mouse_button_released(pr.MouseButton(0)) and self.show and self.show_scale >= 1:
                self.main.send({"minimize_ui": True})

            if pr.is_mouse_button_down(pr.MouseButton(0)):
                frame = 1
        else:
            self.minimize_window_hover = max(self.minimize_window_hover - 1 / 10, 0)

        draw_sprite(self.scroll_bar_sprite, x - self.primary_ui_scale, y - self.primary_ui_scale, self.primary_ui_scale, frame_count=3, current_frame=frame)

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
