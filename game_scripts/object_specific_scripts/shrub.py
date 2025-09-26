import random, math


class Shrub:
    def __init__(self, w, h, player_info):
        self.w = w
        self.h = h

        self.player_info = player_info

        self.variable_pi = 0
        self.popup_scale = 0

        self.destruct = random.randint(60, 1800)

    def step(self, npc, effects, npc_manager):
        general_info = npc["general_info"]

        self.variable_pi += math.pi / 120
        if self.variable_pi >= math.pi * 2:
            self.variable_pi = 0

        self.destruct -= 1

        if self.destruct > 0:
            self.popup_scale = min(self.popup_scale + 1 / 10, 1)
        else:
            self.popup_scale = max(self.popup_scale - 1 / 10, 0)

        general_info["change_scale"] = self.popup_scale
        #general_info["rotation"] = math.sin(self.variable_pi + general_info["x"] / 3) * 5

        if self.destruct <= 0 and self.popup_scale <= 0:
            return 1  # this gets terminated

        return None
