import math


class Item:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.variable_pi = 0
        self.variable_pi2 = 0

        self.popup_scale = 0

        self.occupied = None

        self.picked_up = False
        self.pickup_scale = 1

    def step(self, npc):
        general_info = npc["general_info"]
        scale = general_info["scale"]

        self.variable_pi += math.pi / 40
        if self.variable_pi >= math.pi * 2:
            self.variable_pi = 0

        self.variable_pi2 += math.pi / 30
        if self.variable_pi2 >= math.pi * 2:
            self.variable_pi2 = 0

        # popup
        self.popup_scale = min(self.popup_scale + 1 / 10, 1)
        general_info["change_scale"] = self.popup_scale

        # picked up
        if self.picked_up:
            self.pickup_scale -= 1 / 15

            if self.pickup_scale <= 0:
                return True  # destroy self

        # hover effect
        general_info["y"] = self.h + math.sin(self.variable_pi + general_info["x"] / 3) * scale * 1.5 - (1 - self.pickup_scale) * scale * 4
        general_info["rotation"] = math.sin(self.variable_pi2 + general_info["x"] / 3) * 3

        general_info["alpha"] = self.pickup_scale

        return False
