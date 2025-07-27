import uuid, random, math
from game_scripts.object_specific_scripts.tree import Tree
from game_scripts.object_specific_scripts.item import Item
from game_scripts.object_specific_scripts.storage import Storage


class NPCManager:
    def __init__(self, animations, w, h, player_info, y_offset):
        self.w = w
        self.h = h
        self.y_offset = y_offset

        self.player_info = player_info

        self.animations = animations

        self.npcs = [
            self.create_npc(npc_type="storage_box", coords=[self.w // 2, self.h]),
            self.create_npc(npc_type="longy")
        ]

        # for _ in range(7):
        #     self.npcs.append(self.create_npc(npc_type=random.choice(["pirate_captain", "green_piggy"])))

        self.item_count = 0

    def create_npc(self, npc_type="goblin", coords=None):
        extra_info = self.animations.animation_info[npc_type]["extra_info"]
        parent_type = extra_info.get("parent_type", npc_type)

        if coords is None:
            coords = [random.randint(200, self.w - 100), self.h]

        custom_classes = {
            "node": Tree(self.w, self.h),
            "item": Item(self.w, self.h),
            "storage": Storage(self.w, self.h, self.player_info, self.y_offset)
        }

        return {
            "type": npc_type,
            "parent_type": parent_type,
            "animations": self.animations.animation_info[npc_type]["animations"],  # Shared reference
            "animation_info": {
                "current_frame": 0,
                "current_animation": "idle",

                "animation_speed": extra_info.get("animation_speed", 4),
                "animation_tick": 0
            },
            "general_info": {
                "x": coords[0],
                "y": coords[1],
                "xscale": 1,
                "id": uuid.uuid4(),

                "spd": self.w // 450 * extra_info.get("spd", 1),  # MOVING spd per frame
                "can_carry": extra_info.get("can_carry", True),
                "can_action": extra_info.get("can_action", True),

                "height": extra_info.get("height", self.h // 2),
                "offset_y": extra_info.get("offset_y", 0),
                "origin_point": extra_info.get("origin_point", "middle-center"),
                "scale": extra_info.get("scale", 1),

                "x_original_scale": extra_info.get("x_original_scale", 1),

                "rotation": 0,
                "alpha": 1,
                "change_scale": 1
            },
            "action_info": {
                "doing_action": False,
                "action_value": 0,
                "action_hit": False,
                "action_type": "",

                "pathfinding_values": None,
                "action_cooldown": 0,

                "idle_goal": None,
                "idle_cooldown": 0,
            },
            "custom_class": custom_classes.get(parent_type, None)
        }

    def idle(self, npc):
        actions = npc["action_info"]
        spd = npc["general_info"]["spd"]

        # check if npc is doing any action
        if actions["pathfinding_values"] is None and actions["doing_action"] is False:
            if actions["idle_goal"] is None:
                actions["idle_cooldown"] = max(actions["idle_cooldown"] - 1, 0)

                # assign a random coord for player to travel to
                if actions["idle_cooldown"] <= 0:
                    actions["idle_goal"] = random.randint(150, self.w - 100)
                    actions["idle_cooldown"] = random.randint(30, 180)
            else:
                # if npc arrived at goal, stop
                if abs(npc["general_info"]["x"] - actions["idle_goal"]) <= spd:
                    actions["idle_goal"] = None
                else:
                    npc["general_info"]["x"] += spd * math.copysign(1, actions["idle_goal"] - npc["general_info"]["x"])

    def action(self, npc):
        actions = npc["action_info"]
        info = npc["general_info"]
        animation_info = npc["animation_info"]

        x = info["x"]
        spd = info["spd"]

        pathfinding = actions["pathfinding_values"]

        # check if biome check is in place
        if self.player_info.biome_change:
            self.reset_actions(actions)
            return "biome change in place"

        # check if npc can start new action
        if pathfinding is None and not actions["doing_action"]:
            if actions["action_cooldown"] > 0:
                actions["action_cooldown"] -= 1
                return 0

            # check if npc can CARRY ITEMS
            if info["can_carry"]:
                # find floating items
                storage = None
                potential_items = []

                for obj in self.npcs:
                    if obj["parent_type"] == "storage":
                        storage = obj

                    if obj["parent_type"] == "item":
                        if obj["custom_class"].occupied is None:
                            potential_items.append(obj)

                # storage object exists, lets fucking go
                if storage is not None:
                    if potential_items:
                        closest_items = sorted(potential_items, key=lambda t: abs(x - t["general_info"]["x"]))[:5]
                        actions["pathfinding_values"] = []
                        for item in closest_items:
                            actions["pathfinding_values"].append([item["general_info"]["x"], item, False])
                            item["custom_class"].occupied = npc

                        # after appending all items, append storage
                        actions["pathfinding_values"].append([storage["general_info"]["x"], storage, False])
                        actions["action_type"] = "carrying"

                        return 0

            # check if item limit is not reached
            if self.item_count < 30 and info["can_action"]:
                # find tree
                potential_trees = []
                for potential_tree in self.npcs:
                    if potential_tree["parent_type"] == "node":
                        # check if tree is already occupied
                        if potential_tree["custom_class"].occupied is None:
                            potential_trees.append(potential_tree)

                # if some trees are available, choose the closest one and make it occupied
                if potential_trees:
                    tree = min(potential_trees, key=lambda t: abs(x - t["general_info"]["x"]))
                    actions["pathfinding_values"] = [[tree["general_info"]["x"], tree, False]]  # x, tree
                    tree["custom_class"].occupied = npc

                    actions["action_type"] = "chopping"

                    return 0

            # if no action was found, set an action cooldown
            actions["action_cooldown"] = random.randint(10, 60)
        else:
            if not actions["doing_action"]:
                if actions["action_type"] == "carrying":
                    self.animations.switch_animation(npc, "carry")

                # pathfind to action
                current_path = 0
                for i in range(len(pathfinding)):
                    current_path = i
                    if not pathfinding[i][2]:
                        break

                goal_x = pathfinding[current_path][0]
                obj = pathfinding[current_path][1]

                if actions["action_type"] == "carrying":
                    if abs(goal_x - x) <= spd + 6 * obj["general_info"]["scale"]:
                        pathfinding[current_path][2] = True

                        # check if item was picked up
                        if obj["parent_type"] == "item":
                            obj["custom_class"].picked_up = True

                        # check if storage reached
                        if obj["parent_type"] == "storage":
                            # send all items to storage first
                            for item in pathfinding[:-1]:
                                obj["custom_class"].item_queue.append([item[1]["type"], 1])
                            self.reset_actions(actions)

                else:
                    if abs(goal_x - x) <= spd + 18 * obj["general_info"]["scale"]:
                        actions["doing_action"] = True
                        return 0

                info["x"] += spd * math.copysign(1, goal_x - x)
            else:
                # perform action and then release
                self.animations.switch_animation(npc, "axe")

                frame = animation_info["current_frame"]

                if frame >= 7:
                    target = pathfinding[0][1]

                    if not actions["action_hit"]:
                        actions["action_hit"] = True
                        actions["action_value"] += 0.3  # 4 hits

                        target["custom_class"].hit = 1 / 20

                        if actions["action_value"] >= 1:
                            target["custom_class"].fall = 1 / 10
                            target["custom_class"].fall_side = math.copysign(1, pathfinding[0][0] - x)

                if frame <= 1:
                    actions["action_hit"] = False

                    # and if action was completed, then reset actions
                    if actions["action_value"] >= 1:
                        self.reset_actions(actions)

        return 1

    def reset_actions(self, actions):
        actions["doing_action"] = False
        actions["pathfinding_values"] = None
        actions["action_value"] = 0
        actions["action_type"] = ""
