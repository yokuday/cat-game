import math, random


class Tree:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.occupied = None  # which npc has occupied this tree

        self.hit = 0  # goes from 0 to 1
        self.fall = 0
        self.variable_pi = 0

        self.scale = 0

        self.fall_side = 1

        # used for spawning items
        self.x = 0
        self.y = 0
        self.object_scale = 0

    def step(self, npc, effects):
        general_info = npc["general_info"]
        self.variable_pi += math.pi / 30

        general_info["rotation"] = 0
        if self.hit > 0:
            if self.hit <= 1 / 20:
                effects.add_effect([self.x + random.random(), self.h - 50 * self.object_scale], effect="falling_leaves")

            self.hit += 1 / 20
            general_info["rotation"] = math.sin(self.hit * math.pi * 2) * 5

            if self.hit >= 1:
                self.hit = 0

        if self.fall > 0:
            self.fall += 1 / 12

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

    def terminate(self, npc_manager, effects):
        # item amount to spawn
        item_amount = random.randint(2, 3)

        items_to_spawn = []
        for i in range(item_amount):
            items_to_spawn.append(npc_manager.create_npc("item_wood", coords=[self.x + ((12+i*3) * self.object_scale * self.fall_side), self.h]))

        effects.add_effect([self.x + (15 * self.object_scale * self.fall_side), self.h - 15 * self.object_scale])

        return items_to_spawn
