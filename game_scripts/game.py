import math, random

from game_scripts.animations import GameAnimations
from game_scripts.npc_logic import NPCManager
from game_scripts.ui import MainUI
from game_scripts.visual_scripts.effects_controller import VisualEffects
from ui_menu_files.main_sections.sprite_manager import *

from useful_draw_functions import *


import pyray as pr


class Game:
    def __init__(self, w, h, player_info, ui_window):
        self.w = w
        self.h = h

        self.y_offset = 0

        self.player_info = player_info

        self.font = pr.load_font_ex("content/Roboto-Medium.ttf", 96, None, 0)
        pr.set_texture_filter(self.font.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        # blocks
        self.blocks = {
            "forest": load_sprite("content/biomes/forest/spr_ground.png"),
            "fall_forest": load_sprite("content/biomes/fall_forest/spr_ground.png"),
            "spring_forest": load_sprite("content/biomes/spring_forest/spr_ground.png"),
            "pine_forest": load_sprite("content/biomes/pine_forest/spr_ground.png"),
            "beach": load_sprite("content/biomes/beach/spr_ground.png"),
            "swamp": load_sprite("content/biomes/swamp/spr_ground.png")
        }
        self.block_size = 0.15 * h / self.blocks[player_info.info["current_biome"]].height
        self.y_offset -= self.block_size * self.blocks[player_info.info["current_biome"]].height
        self.shrub_spawn_side = True

        # init everything
        self.animations = GameAnimations(w, h, self.y_offset, player_info)
        self.npc_manager = NPCManager(self.animations, w, h, player_info, self.y_offset)
        self.ui = MainUI(w, h, player_info, ui_window, self.font)
        self.effects = VisualEffects(w, h, player_info, self.y_offset, self)

        # night mode
        self.render_texture = pr.load_render_texture(w, h)
        self.night_mode = False
        self.darkness_level = 0.15

        self.white_mode = False
        self.whiteness = 0
        self.white_shader = pr.load_shader("content/shaders/vertex_shader.frag", "content/shaders/white_shader.frag")
        self.whiteness_loc = pr.get_shader_location(self.white_shader, "whiteness")

        # misc
        self.variable_pi = 0

        self.just_destroyed_items = 5  # 5 frame buffer

    def step(self):
        current_biome = self.player_info.info["current_biome"]

        self.variable_pi += 1 / 60
        if self.variable_pi >= math.pi * 2:
            self.variable_pi -= math.pi * 2

        pr.begin_texture_mode(self.render_texture)
        pr.clear_background(pr.BLANK)

        npcs = self.npc_manager.npcs

        tree_count = 0

        npcs_to_spawn = []

        item_count = sum(1 for npc in npcs if npc.get("parent_type") == "item")
        shrub_count = sum(1 for npc in npcs if npc.get("parent_type") == "shrub")

        self.npc_manager.item_count = item_count

        action_npcs = ["spikey", "shortie", "moppie", "longy", "curly", "bowly",
                       "pirate_captain", "green_piggy", "goblin",

                       "pirate_male", "pirate_female", "orc_male", "orc_female", "angel_male", "angel_female",

                       "enemy_wolf"]

        if self.player_info.biome_destroy_objects:
            self.just_destroyed_items = 5  # 5 frame buffer

        # npc stuff
        npcs_to_pop = []
        for i in range(len(npcs) - 1, -1, -1):
            npc = npcs[i]
            general_info = npc["general_info"]
            action_info = npc["action_info"]
            prev_x = general_info["x"]

            if npc["type"] in action_npcs:
                self.npc_manager.idle(npc)
                self.npc_manager.action(npc)

                # check if enemy died ( lol )
                if general_info["dead"] and general_info["enemy"]:
                    npcs_to_pop.append(i)
                    self.effects.add_effect(
                        [general_info["x"], self.h - 45 * general_info["scale"]])

            if npc["parent_type"] == "node":
                tree_count += 1

            if npc["parent_type"] == "node" or npc["parent_type"] == "item" or npc["parent_type"] == "shrub":
                # check if object has to be terminated
                if self.player_info.biome_destroy_objects:
                    npcs.pop(i)
                    continue

            # custom class stuff
            if npc["custom_class"]:
                terminate = npc["custom_class"].step(npc, self.effects, self.npc_manager)
                if terminate:
                    #npcs.pop(i)
                    npcs_to_pop.append(i)

                    # last terminate call
                    if hasattr(npc["custom_class"], "terminate"):
                        npcs_to_spawn.append(npc["custom_class"].terminate(self.npc_manager, self.effects, current_biome))

                    continue  # skip everything, as npc is terminated

            # npc is moving and NOT doing an action ( AND NPC IS NOTTTTT AN ITEM )
            if not action_info["doing_action"] and npc["parent_type"] != "item":
                if general_info["x"] != prev_x:
                    if action_info["action_type"] != "carrying": self.animations.switch_animation(npc, "run")
                    general_info["xscale"] = math.copysign(1, general_info["x"] - prev_x)
                else:
                    self.animations.switch_animation(npc, "idle")

            self.animations.update_animation(npc)
            self.animations.draw_npc(npc)

            # post step, if item has it
            if npc["custom_class"]:
                if hasattr(npc["custom_class"], "post_step"):
                    npc["custom_class"].post_step(npc)

        for i in npcs_to_pop:
            npcs.pop(i)

        # draw BEFORE visual effects
        self.effects.step(before_step=True)

        # blocks
        b_w = self.blocks[current_biome].width
        b_h = self.blocks[current_biome].height

        decrease_blocks = 1
        offset_blocks = 0

        if current_biome == "beach":
            decrease_blocks = 1.5
            offset_blocks = self.w // 6
        else:
            pass# have BIGGER island
            # decrease_blocks = 1.25
            # offset_blocks = self.w // 12

        block_count = int(self.w // (self.block_size * b_w / 3) // decrease_blocks)
        for a in range(block_count + 1):
            frame = min(a, 1)
            if a == block_count:
                frame = 2

            ch = self.player_info.biome_scale
            offset_ch = 1 - ch

            xx = (a * b_w + b_w * offset_ch / 2) * self.block_size / 3 // 1 + offset_blocks
            yy = self.h - (b_h * self.block_size - b_h * offset_ch / 2)

            draw_sprite(self.blocks[current_biome], xx, yy, self.block_size * 1.05 * ch, current_frame=frame, frame_count=3)

        # draw visual effects
        self.effects.step()

        # if nodes were destroyed, respawn necessary nodes
        if self.just_destroyed_items > -1:
            self.just_destroyed_items -= 1
            if self.just_destroyed_items <= -1:
                # spawn fishing spots
                if current_biome == "beach":
                    npcs.insert(0, self.npc_manager.create_npc("fishing_spot", coords=[self.w // 1.2, self.h]))
                    npcs.insert(0, self.npc_manager.create_npc("fishing_spot", coords=[self.w - self.w // 1.2, self.h]))

        # node stuff
        if not self.player_info.biome_change:
            if tree_count < 20 and (current_biome != "beach" or tree_count < 10):
                if random.random() >= 0.8 + tree_count / 70:
                    npcs.append(self.npc_manager.create_npc(f'{current_biome}_{random.choice(["tree", "stone"])}'))

                    if random.random() < 0.5:
                        pass#npcs.insert(0, self.npc_manager.create_npc(f'enemy_wolf'))

        # shrubbery stuff
        if not self.player_info.biome_change:
            if shrub_count < 5 and (current_biome != "beach" or shrub_count < 3):
                if random.random() >= 0.8 + tree_count / 60:
                    self.shrub_spawn_side = not self.shrub_spawn_side
                    tmp_x = random.randint(0, self.w // 2) if self.shrub_spawn_side else random.randint(self.w // 2, self.w)
                    if current_biome == "beach":
                        tmp_x = random.randint(self.w * 0.2, self.w // 2) if self.shrub_spawn_side else random.randint(self.w // 2, self.w * 0.8)
                    npcs.insert(0, self.npc_manager.create_npc(f'{current_biome}_shrub', coords=[tmp_x, self.h]))
                    # if self.player_info.info["current_biome"] == "forest":
                    #     npcs.insert(0, self.npc_manager.create_npc(random.choice(["grass_1", "grass_2", "grass_3"])))

        # check if there are items to spawn
        # also check if its allowed to create a new item, aka not over item limit
        if len(npcs) < 500:
            for ind in npcs_to_spawn:
                for npc in ind:
                    npcs.insert(0, npc)

        pr.end_texture_mode()

        # night mode
        if self.night_mode:
            # Tint makes everything darker
            tint_value = int(255 * (1 - self.darkness_level))
            tint = pr.Color(tint_value, tint_value, tint_value, 255)
        else:
            tint = pr.WHITE

        # flash speed white mode ( for lightning )
        if self.white_mode:
            pr.begin_shader_mode(self.white_shader)

            pr.set_shader_value(self.white_shader, self.whiteness_loc, pr.ffi.new("float *", self.whiteness),
                                pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        # Draw the render texture with tint
        pr.draw_texture_pro(
            self.render_texture.texture,
            pr.Rectangle(0, 0, self.render_texture.texture.width, -self.render_texture.texture.height),
            pr.Rectangle(0, 0, self.w, self.h),
            pr.Vector2(0, 0),
            0,
            tint
        )
        pr.end_shader_mode()

    def game_ui(self):
        self.ui.field()
