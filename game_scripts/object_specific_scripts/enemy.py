import math, random
import pyray as pr


class Enemy:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.occupied = None  # which npc has occupied this tree

        self.hit = 0  # goes from 0 to 1
        self.fall = 0
        self.variable_pi = 0

        self.scale = 0

        self.timer = 30

    def step(self, npc, effects, npc_manager):
        delta_time = pr.get_frame_time() * 60

        general_info = npc["general_info"]
        self.variable_pi += math.pi / 30

        # set tree growth stage
        frame = self.max_tree_growth - self.current_growth_frame

        if "stone" in npc["type"]:
            frame = self.max_tree_growth - frame
            self.item_type = "stone"

        npc["animation_info"]["current_frame"] = frame
        self.current_growth_time -= delta_time
        if self.current_growth_time <= 0 and self.current_growth_frame < self.max_tree_growth:
            self.current_growth_frame += 1
            self.current_growth_time = random.randint(self.growth_max_time // 2, self.growth_max_time)
            if self.current_growth_frame == self.max_tree_growth:
                self.occupied = None

        general_info["rotation"] = 0
        if self.hit > 0:
            if self.hit <= 1 / 20:
                pass#effects.add_effect([self.x + random.random(), self.h - 50 * self.object_scale], effect="falling_leaves")

            self.hit += 1 / 20
            general_info["rotation"] = math.sin(self.hit * math.pi * 2) * 5

            if self.hit >= 1:
                self.hit = 0

        if self.fall > 0:
            self.fall += 1 / 12 * delta_time

            general_info["rotation"] = (math.pow(self.fall, 3) - 2.5 * math.pow(self.fall, 2) + 1) * self.fall_side * 3
            general_info["alpha"] = min(1 - abs(general_info["rotation"]) / 90, 1)

            if abs(general_info["rotation"]) >= 90:
                return True

        self.scale = min(self.scale + 1 / 10, 1)
        general_info["change_scale"] = self.scale

        if self.x == 0 and self.y == 0 and self.object_scale == 0:
            self.x = general_info["x"]
            self.y = general_info["y"]
            self.object_scale = general_info["scale"]

        return False

    def terminate(self, npc_manager, effects, current_biome):
        # item amount to spawn
        item_amount = random.randint(2, 3)

        items_to_spawn = []
        for i in range(item_amount):
            items_to_spawn.append(npc_manager.create_npc(f"item_{current_biome}_{self.item_type}", coords=[self.x + ((12+i*3) * self.object_scale * self.fall_side), self.h]))

        effects.add_effect([self.x + (15 * self.object_scale * self.fall_side), self.h - 15 * self.object_scale])

        return items_to_spawn
