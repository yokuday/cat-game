from ui_menu_files.sprite_manager import *
from useful_draw_functions import *

import json, math


class ShopSection:
    def __init__(self, border_thickness, w, window_h, p, ui):
        self.row_count = 4
        self.column_count = 2

        self.box_hover_scale = [0 for _ in range(self.row_count * self.column_count)]

        self.p = p
        self.general_info = ui.general_info
        self.font = ui.font

        self.title_font = pr.load_font_ex("content/Notedry.ttf", 96, None, 0)
        pr.set_texture_filter(self.title_font.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.title_font_background = pr.load_font_ex("content/NotedryBase.ttf", 96, None, 0)
        pr.set_texture_filter(self.title_font_background.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.ui = ui

        self.window_h = window_h

        self.border_thickness = border_thickness

        # scroll bar stuff
        self.scroll_bar_width = w // 30
        self.scroll_bar_height = 0.2
        self.scroll = 0  # 0 to 1
        self.scroll_previous = self.scroll

        self.scroll_hover = 0  # check hover

        self.scroll_hold = 0
        self.scroll_clicked_inside_wheel = False
        self.mouse_previous_y = 0

        # sprite stuff
        self.icons = {
            "closed_lock": load_sprite("content/ui/spr_lock_closed_icon.png")
        }

        # shop contents
        file = "content/json_info/ui_info.json"
        with open(file, 'r') as f:
            info = json.load(f)
            f.close()

        file = "content/json_info/npcs.json"
        with open(file, 'r') as f:
            character_info = json.load(f)
            f.close()

        self.info = info["shop_contents"]
        self.animations = {}

        print(character_info)

        # load sprites
        for i in range(len(self.info)):
            self.info[i][1] = load_sprite(self.info[i][1] + ".png")

            # load characters idle animation
            anims = []
            for character in character_info:
                if character == self.info[i][5]:
                    for animation in character_info[character]["animations"]:
                        if "idle" in animation[0]:
                            print(f"{character_info[character]['sprite_folder']}/{animation[1]}.png")
                            tmp = [load_sprite(f"content/{character_info[character]['sprite_folder']}/{animation[1]}.png"),
                                   animation[2], character_info[character]["extra_info"]["height_multiplier"], 0]  # texture, frame_count, height, current_frame
                            anims.append(tmp)
            self.animations[self.info[i][0]] = anims

    def step(self, x, y, w, h, mouse_pos):
        p = w // 40
        x = int(x + p - self.scroll_bar_width)
        y = int(y + p)
        w = int(w - p * 2)
        h = int(h - p * 2)

        box_width = w // 1.4 // self.column_count
        box_height = box_width * 1.25

        box_jump_height = box_height * 1.2
        total_space_taken = max(box_jump_height * self.row_count - h, 0)

        offset_y = total_space_taken * self.get_scroll_value() / (1 - self.scroll_bar_height)

        # fucking LOVE scissor mode
        pr.begin_scissor_mode(x, y, w, h)

        # ui icons
        for i in range(self.row_count):
            for j in range(self.column_count):
                ind = j + i * self.column_count

                box_x = x + w // (self.column_count + 2) * (j*1.8 + 1) - box_width // 2
                box_y = y - offset_y + (box_jump_height * i) + p

                rec = pr.Rectangle(box_x, box_y, box_width, box_height)

                # check hover
                col = blend_colors(GRAY, LIGHTISH_GRAY, self.box_hover_scale[ind])
                if pr.check_collision_point_rec(mouse_pos, rec):
                    self.box_hover_scale[ind] = min(self.box_hover_scale[ind] + 1 / 5, 1)

                    # check if can buy
                    if ind < len(self.info):
                        # check if its purchased already
                        if self.info[ind][4] == 0:
                            if pr.is_mouse_button_pressed(pr.MouseButton(0)):
                                # too expensive
                                if self.general_info["currency"] < self.info[ind][2]:
                                    self.ui.error_shake = 1
                                else:
                                    # can afford
                                    self.ui.success_shake = 1

                                    self.general_info["currency"] -= self.info[ind][2]
                                    self.info[ind][4] += 1
                                    self.ui.main.send({"add_npc": self.info[ind][5]})
                else:
                    self.box_hover_scale[ind] = max(self.box_hover_scale[ind] - 1 / 5, 0)

                pr.draw_rectangle_rounded(rec, 0.2, -1, col)
                pr.draw_rectangle_rounded_lines_ex(rec, 0.25, -1, self.border_thickness, BLACK)

                self.draw_box_contents(ind, box_x, box_y, box_width, box_height)

        pr.end_scissor_mode()

        # scroll bar
        self.scroll_bar(x, y, w, h, p, mouse_pos)

    def scroll_bar(self, x, y, w, h, p, mouse_pos):
        scroll_width = self.scroll_bar_width
        scroll_height = h * 0.9

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

    def draw_box_contents(self, ind, x, y, w, h):
        if ind < len(self.info):
            text = self.info[ind][0]
            sprite = self.info[ind][1]
            price = self.info[ind][2]
            required_level = self.info[ind][3]

            amount_bought = self.info[ind][4]

            # check if level requirement is gut
            if self.general_info["level"] >= required_level:
                # title
                draw_fitted_text(self.title_font, text, x + w // 2, y + h // 20, w // 1.25, 50, BLACK, max_height=h//5, align="center")
                draw_fitted_text(self.title_font_background, text, x + w // 2, y + h // 20, w // 1.25, 50, WHITE,
                                 max_height=h // 5, align="center")

                # character sprite
                if self.animations[text]:
                    for animation in self.animations[text]:
                        char_sprite = animation[0]

                        # move animation forward
                        animation[3] += 1 / 5

                        if animation[3] >= animation[1]:
                            animation[3] = 0

                        current_frame = math.floor(animation[3])

                        sprite_tint = WHITE
                        if amount_bought <= 0:
                            sprite_tint = BLACK

                        scale = h // char_sprite.height * animation[2] * 1.25
                        draw_sprite(char_sprite, x + w // 2, y + h // 2, scale, origin="middle_center", current_frame=current_frame, frame_count=animation[1], tint=sprite_tint)
                
                # price
                txt = "Purchased"
                col = BLACK
                if amount_bought <= 0:
                    txt = f"${price}"
                    col = SOFT_RED
                    if self.general_info["currency"] >= price:
                        col = SOFT_GREEN
                draw_fitted_text(self.font, txt, x + w // 2, y + h // 1.3, w // 1.75, 50, col, max_height=h//6, align="center")
            else:
                rec = pr.Rectangle(x, y, w, h)
                pr.draw_rectangle_rounded(rec, 0.2, -1, DARK_GRAY)

                # lock sprite
                sprite = self.icons["closed_lock"]
                scale = w // sprite.width // 2
                draw_sprite(sprite, x + w // 2, y + h // 3, scale, origin="middle_center")

                # required level text
                text = f"Rec Lv. {required_level}"
                draw_fitted_text(self.font, text, x + w // 2, y + h // 1.4, w // 1.25, 50, WHITE, max_height=h//5, align="center")
