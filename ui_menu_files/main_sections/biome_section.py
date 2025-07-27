import pyray as pr

from ui_menu_files.sprite_manager import draw_sprite
from useful_draw_functions import *


class BiomeSection:
    def __init__(self, border_thickness, w, h, p, ui):
        self.w = w
        self.h = h

        self.p = p

        self.border_thickness = border_thickness

        self.ui = ui
        self.font = ui.font

        self.icons = ui.shop_section.icons

        self.biomes = {
            "forest": [0, 0, SOFT_GREEN, "Forest", 0],  # chosen_scale, hover_scale, b_color, title, required level
            "icy_mountain": [0, 0, LIGHT_BLUE, "Icy Mountain", 5],
            "volcano": [0, 0, SOFT_RED, "Volcano", 20],
            "ocean": [0, 0, BLUE, "Ocean", 100]
        }
        self.current_biome = "forest"

    def step(self, x, y, w, h, mouse_pos):
        b_count = len(self.biomes)

        b_spacing = int(h // b_count)
        b_h = int(b_spacing // 1.35)
        b_w = int(w // 1.25)

        b_padding = b_spacing - b_h

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
            b_col = self.biomes[biome][2]

            size = min(b_scale + b_hover_scale, 1)
            tmp = 20

            extra_h = int(size * b_h // tmp)
            extra_w = int(size * b_w // tmp)

            # background
            yy = int(y + (b_spacing * i * 0.95 + b_padding // 1.25)) - extra_h // 2
            xx = int(x + (w - b_w) // 2) - extra_w // 2
            rec = pr.Rectangle(xx, yy, b_w + extra_w, b_h + extra_h)

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
            col = blend_colors(b_col, GRAY, (1 - size) * 0.8)
            if not unlocked:
                col = GRAY
            pr.draw_rectangle_rounded(rec, 0.3, -1, col)

            col = blend_colors(GRAY, BLACK, b_scale)
            if not unlocked:
                col = DARK_GRAY
            pr.draw_rectangle_rounded_lines_ex(rec, 0.35, -1, self.border_thickness, col)

            if unlocked:
                # biome text
                text = self.biomes[biome][3]
                draw_fitted_text(self.font, text, xx + int((b_w + extra_w) / 2), yy, b_w // 2, 50, BLACK, max_height=b_h // 4, align="center")
            else:
                # closed lock
                sprite = self.icons["closed_lock"]
                scale = b_h // 2 // sprite.height
                draw_sprite(sprite, xx + int((b_w + extra_w) / 2), yy + b_h // 3.5, scale, "middle_center")

                # req level
                text = f"Required Lv. {self.biomes[biome][4]}"
                draw_fitted_text(self.font, text, xx + int((b_w + extra_w) / 2), yy + b_h // 1.5, b_w // 1.5, 50, WHITE, max_height=b_h // 4, align="center")
