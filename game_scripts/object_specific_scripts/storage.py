import pyray as pr


class Storage:
    def __init__(self, w, h):
        self.item_queue = []  # [item name, 1]

    def step(self, npc):
        pass

    def post_step(self, npc):
        general_info = npc["general_info"]
        scale = general_info["scale"]

        i = 0
        while i < len(self.item_queue):
            self.item_queue[i][1] -= 1 / 40

            if self.item_queue[i][1] <= 0.8:
                if self.item_queue[i][1] > 0:
                    p = 1 - self.item_queue[i][1]
                    self.draw_sprite(npc, self.item_queue[i][0], general_info["x"],
                                     general_info["y"] - 30 * scale + (20 * scale * p),
                                     -p * 120, 1 - p, 0.5)
                    i += 1
                else:
                    self.item_queue.pop(i)
            else:
                break

    def draw_sprite(self, npc, item_name, x, y, angle, alpha, image_scale):
        current_anim = npc["animations"][item_name]
        general_info = npc["general_info"]

        frame_width = current_anim["frame_width"]

        source_rect = pr.Rectangle(
            0, 0,
            frame_width,
            current_anim["texture"].height
        )

        # scale and size
        scale = general_info["height"] / current_anim["texture"].height * image_scale
        scaled_width = frame_width * scale
        scaled_height = general_info["height"] * image_scale

        # destination rectangle ( drawing from center )
        dest_rect = pr.Rectangle(
            x, y,
            scaled_width, scaled_height
        )

        # origin point (center of the sprite)
        origin = pr.Vector2(scaled_width / 2, scaled_height / 2)

        color = pr.Color(255, 255, 255, int(alpha * 255))
        pr.draw_texture_pro(current_anim["texture"], source_rect, dest_rect,
                            origin, angle, color)
