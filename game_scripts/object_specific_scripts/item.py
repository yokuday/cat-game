import math


def parabolic_height(frame, target_height=6, max_height=10, total_frames=15):
    last_frame = total_frames - 1

    b = 2 * max_height / last_frame * (2 - target_height / max_height) ** 0.5
    a = (target_height - b * last_frame) / (last_frame ** 2)

    return a * frame ** 2 + b * frame


class Item:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.variable_pi = 0
        self.variable_pi2 = 0

        self.popup_scale = 0

        self.occupied = None

        self.picked_up = False
        self.pickup_scale = 0

        self.npc_info = None
        self.npc_animation_info = None
        self.deposited = False
        self.number = 0

        self.change_x = 0  # self.x and npc.x
        self.old_x = 0

        self.height = 6

        self.original_x = None
        self.npc_jumping_frames = [2, 4, 4, 0, 1, 4, 4, 0, 2]
        self.max_animation_tick = 5

    def step(self, npc, effects, npc_manager):
        general_info = npc["general_info"]
        scale = general_info["scale"]

        if self.original_x is None:
            self.original_x = general_info["x"]

        self.variable_pi += math.pi / 40
        if self.variable_pi >= math.pi * 2:
            self.variable_pi = 0

        self.variable_pi2 += math.pi / 30
        if self.variable_pi2 >= math.pi * 2:
            self.variable_pi2 = 0

        # popup
        if "fish" in npc["type"]:
            self.popup_scale = 1

        self.popup_scale = min(self.popup_scale + 1 / 10, 1)
        general_info["change_scale"] = self.popup_scale

        general_info["y"] = self.h

        # picked up
        if self.picked_up:
            if self.pickup_scale <= 0:
                self.change_x = (self.npc_info["x"] - general_info["x"]) / 15 + (self.number - 2) * scale / 15 * 3
                self.old_x = self.npc_info["x"]

            self.pickup_scale = min(self.pickup_scale + 1 / 15, 1)

            # parabolaaaaa baby
            if self.pickup_scale < 1:
                general_info["x"] += self.change_x
            general_info["y"] -= parabolic_height(int(self.pickup_scale * 15), target_height=8, max_height=15) * scale

            # follow npc
            general_info["x"] -= self.old_x - self.npc_info["x"]
            self.old_x = self.npc_info["x"]

            # follow npc jumping
            in_between_value = 0#self.npc_animation_info["animation_tick"] / self.max_animation_tick * (self.npc_jumping_frames[self.npc_animation_info["current_frame"]] - self.npc_jumping_frames[self.npc_animation_info["current_frame"] + 1])
            general_info["y"] -= (self.npc_jumping_frames[self.npc_animation_info["current_frame"]] - in_between_value) * scale

            if self.deposited:
                return True  # destroy self

        general_info["rotation"] = math.sin(self.variable_pi2 + self.original_x / 3) * 3

        if not self.pickup_scale:
            general_info["y"] += math.sin(self.variable_pi + self.original_x / 3) * scale * 1.5

        #general_info["alpha"] = 1 - self.pickup_scale

        return False
