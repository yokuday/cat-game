from ui_menu_files.main_sections.sprite_manager import *
from ui_menu_files.main_sections.scrollbar import Scrollbar
from useful_draw_functions import *

import json, math


class ShopSection:
    def __init__(self, border_thickness, w, window_h, p, ui):
        self.row_count = 5
        self.column_count = 3

        self.box_hover_scale = [0 for _ in range(self.row_count * self.column_count)]

        self.p = p
        self.general_info = ui.general_info
        self.font = ui.font

        self.title_font = pr.load_font_ex("content/Notedry.ttf", 96, None, 0)
        pr.set_texture_filter(self.title_font.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.title_font_background = pr.load_font_ex("content/NotedryBase.ttf", 96, None, 0)
        pr.set_texture_filter(self.title_font_background.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.ui = ui

        self.coords = ui.coords
        self.scrollbar_sprite = ui.scroll_bar_sprite
        self.sc = ui.primary_ui_scale

        self.window_h = window_h
        self.border_thickness = border_thickness

        # scroll bar stuff
        self.scrollbar = Scrollbar(w, border_thickness, self.row_count, self.coords, self.scrollbar_sprite)

        # sprite stuff
        self.icons = {
            "closed_lock": load_sprite("content/ui/spr_lock_closed_icon.png"),
        }

        # frames
        self.frames = load_sprite("content/ui/elements/spr_small_frames.png")

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

        # some animations for info
        self.info_anim = []
        for i in range(len(self.info)):
            self.info_anim.append([0, 0])  # switch animation, switch hover

    def step(self, mouse_pos):
        scroll_bar_height = self.scrollbar.scroll_bar_height

        x, w, y, h = get_coord_values(self.coords["main_area"])

        box_width = self.sc * self.frames.width / 4
        box_height = self.sc * self.frames.height

        box_jump_height = box_height
        total_space_taken = max(box_jump_height * self.row_count - h + self.border_thickness, 0)

        offset_y = total_space_taken * self.scrollbar.get_scroll_value() / (1 - scroll_bar_height)

        # fucking LOVE scissor mode
        pr.begin_scissor_mode(x, y, w, h)

        skip_icon = 0  #  if npc is bought, DONT SHOW IT ANYMORE

        # ui icons
        for i in range(self.row_count):
            for j in range(self.column_count):
                ind = j + i * self.column_count + skip_icon

                while True:
                    if ind < len(self.info):
                        if self.info[ind][4] >= 1:
                            skip_icon += 1
                            ind = j + i * self.column_count + skip_icon
                        else:
                            break
                    else:
                        break

                if ind > self.column_count * self.row_count - 1:
                    continue

                box_x = x + box_width * j + self.sc * 2
                box_y = y - offset_y + (box_jump_height * i) + 0 + self.sc

                rec = pr.Rectangle(box_x, box_y, box_width, box_height)

                # check hover
                col = blend_colors(LIGHT_GRAY, LIGHTISH_GRAY, self.box_hover_scale[ind])
                if pr.check_collision_point_rec(mouse_pos, rec):
                    self.box_hover_scale[ind] = min(self.box_hover_scale[ind] + 1 / 5, 1)

                    # check if can buy
                    if ind < len(self.info):
                        # check if its purchased already AND if level requirement is met
                        if self.info[ind][4] == 0 and self.general_info["level"] >= self.info[ind][3]:
                            if pr.is_mouse_button_pressed(pr.MouseButton(0)):
                                # too expensive
                                if self.general_info["currency"] < self.info[ind][2]:
                                    self.ui.error_shake = 1
                                else:
                                    # can afford
                                    self.ui.success_shake = 1

                                    self.general_info["currency"] -= self.info[ind][2]
                                    self.info[ind][4] += 1

                                    self.info[ind][6] = 1  # set character to true
                                    self.ui.main.send({"add_npc": self.info[ind][5]})

                                    skip_icon += 1
                                    continue
                else:
                    self.box_hover_scale[ind] = max(self.box_hover_scale[ind] - 1 / 5, 0)

                tw = self.frames.width / 4 * (self.box_hover_scale[ind] / 50)
                th = self.frames.height * (self.box_hover_scale[ind] / 50)
                tmp = (1 + self.box_hover_scale[ind] / 50)

                draw_sprite(self.frames, box_x - tw, box_y - th, self.sc * tmp, frame_count=4, current_frame=0)

                self.draw_box_contents(ind, box_x - tw, box_y - th, box_width * tmp, box_height * tmp, mouse_pos)

        pr.end_scissor_mode()

        # scroll bar
        self.scrollbar.scroll_bar(mouse_pos)

    def draw_box_contents(self, ind, x, y, w, h, mouse_pos):
        if ind < len(self.info):
            text = self.info[ind][0]
            sprite = self.info[ind][1]
            price = self.info[ind][2]
            required_level = self.info[ind][3]

            amount_bought = self.info[ind][4]

            character_added = self.info[ind][6]

            switch_scale = self.info_anim[ind][0]
            switch_hover = self.info_anim[ind][1]

            # check if level requirement is gut
            if self.general_info["level"] >= required_level:
                # title
                # draw_fitted_text(self.title_font, text, x + w // 2, y + h // 20, w // 1.25, 50, BLACK, max_height=h//5, align="center")
                # draw_fitted_text(self.title_font_background, text, x + w // 2, y + h // 20, w // 1.25, 50, WHITE,
                #                  max_height=h // 5, align="center")

                # character sprite
                if self.animations[text]:
                    for animation in self.animations[text]:
                        char_sprite = animation[0]

                        # move animation forward
                        animation[3] += 1 / 5

                        if animation[3] >= animation[1]:
                            animation[3] = 0

                        current_frame = math.floor(animation[3])

                        hover = self.box_hover_scale[ind]

                        sprite_tint = BLACK
                        if price <= self.general_info["currency"]:
                            sprite_tint = blend_colors(BLACK, GREEN, hover)

                        scale = h // char_sprite.height * animation[2] * 1.25
                        draw_sprite(char_sprite, x + w // 2, y + h // 2.25, scale, origin="middle_center", current_frame=current_frame, frame_count=animation[1], tint=sprite_tint)
                
                # price
                if amount_bought <= 0:
                    a_y = y + h - h // 4.5
                    a_h = int(h // 6)

                    # actual price
                    txt = str(price)
                    col = BLACK
                    draw_fitted_text(self.font, txt, x + w // 2, a_y + a_h // 2, w // 1.75, 50, col, max_height=h//6, align="center", center_y=True)
                else:
                    # switch
                    if character_added:
                        self.info_anim[ind][0] = min(switch_scale + 1 / 10, 1)
                    else:
                        self.info_anim[ind][0] = max(switch_scale - 1 / 10, 0)

                    # switch coordinates and info
                    hh = h // 7
                    ww = w // 2

                    xx = int(x + w // 2)
                    yy = int(y + h // 1.2)

                    rad = int(hh // 2.5)
                    pad = int((hh - rad) // 2)

                    rec = pr.Rectangle(xx - ww // 2, yy - hh // 2, ww, hh)

                    # switch hover and activate / deactivate
                    if pr.check_collision_point_rec(mouse_pos, rec):
                        if pr.is_mouse_button_pressed(pr.MouseButton(0)) and (self.info_anim[ind][0] >= 1 or self.info_anim[ind][0] <= 0):
                            self.info[ind][6] = not character_added
                            if self.info[ind][6]:
                                self.ui.main.send({"add_npc": self.info[ind][5]})
                            else:
                                self.ui.main.send({"remove_npc": self.info[ind][5]})

                        self.info_anim[ind][1] = min(switch_hover + 1 / 5, 1)
                    else:
                        self.info_anim[ind][1] = max(switch_hover - 1 / 5, 0)

                    # draw switch background
                    col = blend_colors(SOFT_RED, SOFT_GREEN, switch_scale)
                    pr.draw_rectangle_rounded(rec, 0.75, -1, col)
                    pr.draw_rectangle_rounded_lines_ex(rec, 0.8, -1, int(hh // 15), BLACK)

                    # draw circle
                    c_x = int(rad + xx - ww // 2 + pad // 1.25)
                    extra_x = int(switch_scale * (ww - (rad + pad) * 2))

                    pr.draw_circle(c_x + extra_x, yy, int(rad * (1 + switch_hover / 5)), BLACK)
                    pr.draw_circle(c_x + extra_x, yy, rad, WHITE)

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
