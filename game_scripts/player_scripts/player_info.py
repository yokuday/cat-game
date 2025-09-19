import json


class PlayerInfo:
    def __init__(self, ui_window):
        file = "player_info.json"

        self.ui_window = ui_window

        try:
            with open(file, 'r') as f:
                self.info = json.load(f)
        except:
            self.info = {
                "current_level": 2,
                "current_exp": 0,
                "currency": 200,

                "current_biome": "pine_forest"
            }

        # send current info
        self.ui_window.prepare_to_send({"current_level": self.info["current_level"], "currency": self.info["currency"],
                                        "current_biome": self.info["current_biome"]})

        self.info["required_exp"] = self.get_exp_requirement()

        # biome animation
        self.next_biome = None
        self.biome_scale = 0
        self.biome_change = False
        self.biome_destroy_objects = False

    def get_exp_requirement(self):
        level = self.info["current_level"]

        # 3 stages
        if level < 10:
            return 10 + level * 10
        if level < 100:
            return level * 25 - 150
        return level * 50 - 2500

    def add_exp(self, amount):
        self.info["current_exp"] += amount

        while True:
            if self.info["current_exp"] >= self.info["required_exp"]:
                self.info["current_exp"] -= self.info["required_exp"]
                self.info["current_level"] += 1
                self.info["required_exp"] = self.get_exp_requirement()

                self.ui_window.prepare_to_send({"current_level": self.info["current_level"]})
            else:
                break

    def step(self):
        # biome changing
        if self.next_biome:
            self.biome_change = True

            if self.biome_scale > 0:
                self.biome_scale = max(self.biome_scale - 1 / 15, 0)
            else:
                self.info["current_biome"] = self.next_biome
                self.next_biome = None
                self.biome_destroy_objects = True  # destroy all biome related objects
        else:
            self.biome_destroy_objects = False
            if self.biome_scale < 1:
                self.biome_scale = min(self.biome_scale + 1 / 15, 1)
            else:
                self.biome_change = False
