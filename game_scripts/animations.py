import pyray as pr
import random, json


class GameAnimations:
    def __init__(self, w, h, y_offset, player_info):
        self.w = w
        self.h = h
        self.y_offset = y_offset

        self.animation_info = {}
        self.initialize_animation_info()

        self.player_info = player_info

    def initialize_animation_info(self):
        json_files = [
            "content/json_info/npcs.json",
            "content/json_info/nodes.json",
            "content/json_info/items.json",
            "content/json_info/shrubs.json"
        ]

        self.animation_info = self.load_animation_info(json_files)

        for key in self.animation_info:
            try:
                a = self.animation_info[key]
                a["extra_info"]["scale"] = a["extra_info"]["height"] / a["animations"]["idle"]["texture"].height
            except:
                pass

    def load_animation_info(self, json_file_paths):
        combined_config = {}

        for file_path in json_file_paths:
            with open(file_path, 'r') as file:
                config = json.load(file)
                combined_config.update(config)

        animation_info = {}

        # first pass through to get all animation shiii
        for entity_name, entity_data in combined_config.items():
            animations = self.load_animations(
                entity_data["sprite_folder"],
                entity_data["animations"]
            )
            extra_info = entity_data["extra_info"].copy()

            included_animations = entity_data.pop("included_animations", None)

            # handle height calculations
            if "height_multiplier" in extra_info:
                multiplier = extra_info.pop("height_multiplier")
                height_source = extra_info.pop("height_source", "h")

                if height_source == "h":
                    extra_info["height"] = int(self.h * multiplier)

            animation_info[entity_name] = {
                "animations": animations,
                "extra_info": extra_info,

                "file_info": [entity_data["sprite_folder"], entity_data["animations"][0][1], entity_data["animations"][0][2]],  # very fucking ugly, lets hope items only need idle animation
                "included_animations": included_animations,
            }

        # second passthrough for items, that required all other items to be loaded first
        for key in animation_info:
            if animation_info[key]["included_animations"]:
                for key2 in animation_info:
                    for item in animation_info[key]["included_animations"]:
                        if animation_info[key2]["extra_info"].get("parent_type", None) == item:
                            anim_name = key2
                            file_info = animation_info[key2]["file_info"]

                            texture = pr.load_texture(f"content/{file_info[0]}/{file_info[1]}.png")
                            animation_info[key]["animations"][anim_name] = {
                                "texture": texture,
                                "frames": file_info[2],
                                "frame_width": texture.width // file_info[2]
                            }
                            continue

        return animation_info

    def load_animations(self, folder, animations_data):
        animations = {}

        for anim_name, file_name, frame_count in animations_data:
            texture = pr.load_texture(f"content/{folder}/{file_name}.png")

            animations[anim_name] = {
                "texture": texture,
                "frames": frame_count,
                "frame_width": texture.width // frame_count
            }

        return animations

    def update_animation(self, npc):
        anim_info = npc["animation_info"]

        if anim_info["animation_speed"] != -1:  # -1 animation means NO animation
            anim_info["animation_tick"] += 1
            if anim_info["animation_tick"] >= anim_info["animation_speed"]:
                anim_info["animation_tick"] = 0
                current_anim = npc["animations"][anim_info["current_animation"]]
                anim_info["current_frame"] = (anim_info["current_frame"] + 1) % current_anim["frames"]

    def switch_animation(self, npc, new_animation):
        if new_animation in npc["animations"] and new_animation != npc["animation_info"]["current_animation"]:
            npc["animation_info"]["current_animation"] = new_animation
            npc["animation_info"]["current_frame"] = 0

    def draw_npc(self, npc):
        anim_info = npc["animation_info"]

        current_animation = anim_info["current_animation"]

        # check if there are additional animations that need to be stacked
        current_animations = []
        for potential_animation in npc["animations"]:
            if potential_animation != current_animations:
                if current_animation in potential_animation:
                    current_animations.append(potential_animation)

        current_animations.insert(0, current_animation)

        for animation in current_animations:
            current_anim = npc["animations"][animation]
            general_info = npc["general_info"]

            offset_y = general_info["offset_y"]

            if current_animation in anim_info["animation_offsets"]:
                offset_y = anim_info["animation_offsets"][current_animation]

            origin_point = general_info["origin_point"]
            rotation = general_info["rotation"]
            alpha = general_info["alpha"]
            change_scale = general_info["change_scale"]

            frame_width = current_anim["frame_width"]

            # biome change scale
            if self.player_info.biome_change:
                if npc["parent_type"] == "node" or npc["parent_type"] == "item" or npc["parent_type"] == "shrub":
                    change_scale = change_scale * self.player_info.biome_scale

            # source rectangle
            source_rect = pr.Rectangle(
                anim_info["current_frame"] * frame_width, 0,
                frame_width * general_info.get("xscale", 1) * general_info.get("x_original_scale", 1),  # flip width if xscale is -1
                current_anim["texture"].height
            )

            # scale and size
            scale = general_info["height"] / current_anim["texture"].height * change_scale
            scaled_width = frame_width * scale
            scaled_height = general_info["height"] * change_scale

            # destination rectangle ( drawing from center )
            dest_rect = pr.Rectangle(
                general_info["x"], general_info["y"] - offset_y * scale + self.y_offset,
                scaled_width, scaled_height
            )

            # origin point (center of the sprite)
            origin = pr.Vector2(scaled_width / 2, scaled_height / 2)

            if origin_point == "middle-bottom":
                origin = pr.Vector2(scaled_width / 2, scaled_height)

            color = pr.Color(255, 255, 255, int(alpha * 255))
            pr.draw_texture_pro(current_anim["texture"], source_rect, dest_rect,
                                origin, rotation, color)
