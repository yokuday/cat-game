import pyray as pr

from ui_menu_files.main_sections.sprite_manager import draw_sprite, load_sprite
from ui_menu_files.main_sections.scrollbar import Scrollbar

from useful_draw_functions import *


class BiomeSection:
    def __init__(self, border_thickness, w, h, p, ui):
        self.w = w
        self.h = h

        self.p = p

        self.border_thickness = border_thickness

        self.ui = ui
        self.coords = ui.coords
        self.sc = ui.primary_ui_scale

        self.font = ui.font

        self.icons = ui.shop_section.icons

        self.biomes = {
            "forest": [0, 0, SOFT_GREEN, "Forest", 0],  # chosen_scale, hover_scale, b_color, title, required level
            "icy_mountain": [0, 0, LIGHT_BLUE, "Icy Mountain", 0],
            "volcano": [0, 0, SOFT_RED, "Volcano", 20],
            "ocean": [0, 0, BLUE, "Ocean", 100]
        }
        self.current_biome = "forest"

        # biome frames
        self.frames = load_sprite("content/ui/elements/spr_biome_frames.png")
        self.scrollbar_sprite = ui.scroll_bar_sprite

        self.scrollbar = Scrollbar(w, border_thickness, len(self.biomes), self.coords, self.scrollbar_sprite)

    def step(self, mouse_pos):
        x, w, y, h = get_coord_values(self.coords["main_area"])
        pr.begin_scissor_mode(int(x), int(y), int(w), int(h))

        scroll_bar_height = self.scrollbar.scroll_bar_height

        b_h = self.sc * self.frames.height
        b_w = self.sc * self.frames.width / 2

        b_spacing = b_h

        offset_y = (h - b_spacing * len(self.biomes)) * self.scrollbar.get_scroll_value() / (1 - scroll_bar_height)

        for i, biome in enumerate(self.biomes):
            unlocked = False
            if self.ui.general_info["level"] >= self.biomes[biome][4]:
                unlocked = True

            # chosen scale
            if self.current_biome == biome:
                self.biomes[biome][0] = min(self.biomes[biome][0] + 1 / 10, 1)
            else:
                self.biomes[biome][0] = max(self.biomes[biome][0] - 1 / 10, 0)

            # vars
            b_scale = self.biomes[biome][0]
            b_hover_scale = self.biomes[biome][1]

            # background
            yy = y + b_spacing * i + offset_y
            rec = pr.Rectangle(x, yy, b_w, b_h)

            # hover scale
            if pr.check_collision_point_rec(mouse_pos, rec) and unlocked:
                self.biomes[biome][1] = min(b_hover_scale + 1 / 10, 1)

                # check click
                if b_scale <= 0 and pr.is_mouse_button_pressed(pr.MouseButton(0)):
                    self.current_biome = biome
                    self.ui.main.send({"current_biome": biome})
            else:
                self.biomes[biome][1] = max(b_hover_scale - 1 / 10, 0)

            # drawing background
            frame = 0
            if b_scale > 0:
                frame = 1
            draw_sprite(self.frames, x, yy, self.sc, current_frame=frame, frame_count=2)

            if unlocked:
                # biome text
                text = self.biomes[biome][3]
                draw_fitted_text(self.font, text, x + int(b_w / 2), yy + b_h // 2.25, b_w // 2, 50, BLACK, max_height=b_h // 1.75, align="center", center_y=True)
            else:
                # closed lock
                sprite = self.icons["closed_lock"]
                scale = b_h // 1.5 // sprite.height
                draw_sprite(sprite, x + int(b_w / 2), yy + b_h // 2.5, scale, "middle_center")

                s_w = b_w // 5.75
                s_h = b_h // 3.5

                s_x = x + b_w // 2
                s_y = yy + b_h - s_h // 2

                # req level
                text = f"Lv. {self.biomes[biome][4]}"
                draw_fitted_text(self.font, text, s_x, s_y, s_w // 1.25, 50, BLACK, max_height=s_h // 1.5, align="center", center_y=True)

        pr.end_scissor_mode()

        self.scrollbar.scroll_bar(mouse_pos)
