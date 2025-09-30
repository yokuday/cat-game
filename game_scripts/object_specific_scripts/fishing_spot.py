import math, random
import pyray as pr


class FishingSpot:
    def __init__(self, w, h, player_info, y_offset):
        self.w = w
        self.h = h

        self.occupied = None  # which npc has occupied this tree

        self.hit = 0  # goes from 0 to 1
        self.fall = 0
        self.fling = 0  # fish flinging
        self.fling_random_offset = 0
        self.variable_pi = 0

        self.fling_side = 1

        # used for spawning items
        self.x = 0
        self.y = 0
        self.object_scale = 0

        self.player_info = player_info
        self.y_offset = y_offset

        self.item_name = "item_beach_fish"

    def step(self, npc, effects, npc_manager):
        delta_time = pr.get_frame_time() * 60

        general_info = npc["general_info"]
        scale = general_info["scale"]
        self.variable_pi += math.pi / 30

        # start flinging fish out / can continue fishing
        if self.fall > 0:
            self.fall = 0
            self.occupied = None
            self.hit = 0

            if self.fling <= 0:
                self.fling = 1
                self.fling_random_offset = random.uniform(0.5, 1.5)

                # splash effect
                effects.waves.add_ripple(general_info["x"] + self.y_offset * 2 * self.fling_side * -1)

        general_info["change_scale"] = 0

        # fish flinging
        if self.fling > 0:
            self.fling -= 0.02 * delta_time

            val = (max(self.fling, 0) - 0.5) * 2
            cropped_val = min(val, 0)

            x = general_info["x"] + self.y_offset * 2 * self.fling_side * val * -1 - cropped_val * self.fling_side * self.y_offset * self.fling_random_offset
            y = general_info["y"] + self.y_offset * 2 * (1 - val * val) - self.y_offset * val + cropped_val * self.y_offset * 0.2

            if val <= -1:
                # SPAWN FISH
                npc_manager.npcs.insert(0, npc_manager.create_npc(
                    self.item_name, coords=[x, self.h]))

                return False

            self.draw_sprite(npc, self.item_name, x, y, (val + 1) * 30 * self.fling_side, 1, 1)

        if self.x == 0 and self.y == 0 and self.object_scale == 0:
            self.x = general_info["x"]
            self.y = general_info["y"]
            self.object_scale = general_info["scale"]

            if self.x < self.w / 2:
                self.fling_side = -1

        return False

    def draw_sprite(self, npc, item_name, x, y, angle, alpha, image_scale):
        current_anim = npc["animations"][item_name]
        general_info = npc["general_info"]

        frame_width = current_anim["frame_width"]

        source_rect = pr.Rectangle(
            0, 0,
            frame_width,
            current_anim["texture"].height
        )

        scale = general_info["height"] / current_anim["texture"].height * image_scale
        scaled_width = frame_width * scale
        scaled_height = general_info["height"] * image_scale

        dest_rect = pr.Rectangle(
            x, y + self.y_offset,
            scaled_width, scaled_height
        )

        origin = pr.Vector2(scaled_width / 2, scaled_height / 2)

        color = pr.Color(255, 255, 255, int(alpha * 255))
        pr.draw_texture_pro(current_anim["texture"], source_rect, dest_rect,
                            origin, angle, color)
