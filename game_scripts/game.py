import math, random

from game_scripts.animations import GameAnimations
from game_scripts.npc_logic import NPCManager
from game_scripts.ui import MainUI

import pyray as pr


class Game:
    def __init__(self, w, h, player_info, ui_window):
        self.w = w
        self.h = h

        self.y_offset = 0

        self.player_info = player_info

        self.font = pr.load_font_ex("content/Roboto-Medium.ttf", 96, None, 0)
        pr.set_texture_filter(self.font.texture, pr.TextureFilter.TEXTURE_FILTER_BILINEAR)

        # init everything
        self.animations = GameAnimations(w, h, self.y_offset)
        self.npc_manager = NPCManager(self.animations, w, h, player_info, self.y_offset)
        self.ui = MainUI(w, h, player_info, ui_window, self.font)

    def step(self):
        npcs = self.npc_manager.npcs

        tree_count = 0

        npcs_to_spawn = []

        # npc stuff
        for i in range(len(npcs) - 1, -1, -1):
            npc = npcs[i]
            general_info = npc["general_info"]
            action_info = npc["action_info"]
            prev_x = general_info["x"]

            action_npcs = ["spikey", "shortie", "moppie", "longy", "curly", "bowly"]

            if npc["type"] in action_npcs:
                self.npc_manager.idle(npc)
                self.npc_manager.action(npc)

            if npc["parent_type"] == "tree":
                tree_count += 1

            # custom class stuff
            if npc["custom_class"]:
                terminate = npc["custom_class"].step(npc)
                if terminate:
                    npcs.pop(i)

                    # last terminate call
                    if hasattr(npc["custom_class"], "terminate"):
                        npcs_to_spawn.append(npc["custom_class"].terminate(self.npc_manager))

                    continue  # skip everything, as npc is terminated

            # npc is moving and NOT doing an action
            if not action_info["doing_action"]:
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

        # node stuff
        if tree_count < 10:
            if random.random() <= 0.02:
                npcs.append(self.npc_manager.create_npc(random.choice(["oak_tree", "birch_tree"])))

        # check if there are items to spawn
        # also check if its allowed to create a new item, aka not over item limit
        if len(npcs) < 500:
            for ind in npcs_to_spawn:
                for npc in ind:
                    npcs.insert(0, npc)

    def game_ui(self):
        self.ui.field()
