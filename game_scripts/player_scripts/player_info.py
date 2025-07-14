import json


class PlayerInfo:
    def __init__(self):
        file = "player_info.json"

        try:
            with open(file, 'r') as f:
                self.info = json.load(f)
        except:
            self.info = {
                "current_level": 0,
                "current_exp": 0
            }

        self.info["required_exp"] = self.get_exp_requirement()

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

        if self.info["current_exp"] >= self.info["required_exp"]:
            self.info["current_exp"] -= self.info["required_exp"]
            self.info["current_level"] += 1
            self.info["required_exp"] = self.get_exp_requirement()
