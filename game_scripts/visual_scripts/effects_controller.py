import pyray as pr
from useful_draw_functions import *

import math, random


class VisualEffects:
    def __init__(self, w, h, player_info):
        self.w = w
        self.h = h

        self.player_info = player_info

        self.scale = 0
        self.current_effects = [""]
        self.next_effects = None

        self.size = max(int(h // 75), 1)

        image = pr.gen_image_color(self.size, self.size, WHITE)
        self.pixel = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.gen_image_color(max(int(self.size // 2), 1), int(self.size * 3), WHITE)
        self.tall_pixel = pr.load_texture_from_image(image)
        pr.unload_image(image)

        self.max_effect_count = 50
        self.effect_count = self.max_effect_count

        # setu fireflies
        self.firefly_info = []
        for _ in range(self.max_effect_count):
            self.firefly_info.append([
                [random.randint(0, w), random.randint(0, h)],
                [random.randint(0, w), random.randint(0, h)],
                random.randint(30, 180),
                random.randrange(self.size, self.size * 10),
                random.random() * math.pi, random.random()
            ])  # [x, y], target [x, y], decide different target, spd, glow, glow_offset

        self.rain_info = []
        for _ in range(self.max_effect_count):
            self.rain_info.append([
                random.randint(-50, w + 50),
                random.randint(-200, h),
                random.uniform(self.size, self.size * 2) * 2,
                random.uniform(0.5, 1.2),
                random.uniform(-15, -25)
            ])  # [x, y, speed, scale, rotation]

        self.snow_info = []
        for _ in range(self.max_effect_count * 2):
            self.snow_info.append([
                random.randint(-50, w + 50),  # x position
                random.randint(-200, h),  # y position
                random.uniform(self.size, self.size * 3) / 8,  # speed
                random.uniform(0.75, 2.5),
                random.uniform(-0.3, 0.3)  # horizontal drift
            ])

        # VOLCANO
        self.lava_pops_info = []
        for _ in range(self.max_effect_count):
            self.lava_pops_info.append([
                random.randint(-50, w + 50),  # x position
                random.randint(h + self.size, h + self.size * 4),  # y position
                random.uniform(self.size / 2, self.size),  # size
                random.uniform(self.size, self.size * 10),  # height speed
                random.uniform(-1, 1)  # horizontal drift
            ])

        self.effects = {
            "fireflies": self.fireflies,
            "rain": self.rain,
            "snow": self.snow,
            "lava pops": self.lava_pops
        }

        self.biome_effects = {
            "forest": ["rain", "fireflies"],
            "icy_mountain": ["snow"],
            "volcano": ["lava pops"],
            "ocean": [""]
        }

        # set initial effect for biome
        self.set_effects(self.player_info.info["current_biome"])

        self.variable_pi = 0

    def step(self):
        self.variable_pi += 1 / 1000
        if self.variable_pi >= 2 * math.pi:
            self.variable_pi -= 2 * math.pi

        if self.next_effects:
            if self.scale > 0:
                self.scale = max(self.scale - 1 / 15, 0)
            else:
                self.current_effects = self.next_effects
                self.next_effects = None
        else:
            self.scale = min(self.scale + 1 / 15, 1)

        # draw visual effects
        if self.scale > 0:
            for effect in self.current_effects:
                if self.effects.get(effect):
                    self.effects[effect]()

    def fireflies(self):
        for i in range(self.effect_count):
            info = self.firefly_info[i]

            spd = info[3] / 75
            glow = info[4]

            x = int(info[0][0])
            y = int(info[0][1])

            # set different target location
            info[2] -= 1
            if info[2] <= 0:
                info[2] = random.randint(30, 180) * 10
                info[1] = [max(min(random.randrange(x-int(self.w / 5), x+int(self.w / 5)), self.w), 0), max(min(random.randrange(y-int(self.h / 5), y+int(self.h / 5)), self.h), 0)]

            # set dir
            if abs(info[0][0] - info[1][0]) > spd * 2:
                info[0][0] += self.lengthdir_x(spd, info[0], info[1])
            if abs(info[0][1] - info[1][1]) > spd * 2:
                info[0][1] += self.lengthdir_y(spd, info[0], info[1])

            val = abs(math.sin(self.variable_pi + i))
            val2 = math.sin(self.variable_pi * 8 + i + glow * self.size) * self.size * glow / 3

            pr.draw_texture_ex(self.pixel, pr.Vector2(x + int(val2), y), 0, self.scale, blend_colors(BLACK, YELLOW, val))

    def rain(self):
        for i in range(self.effect_count):
            info = self.rain_info[i]

            # Update position
            info[1] += info[2]
            info[0] += info[2] * 0.2

            # Reset raindrop when it goes off screen
            if info[1] > self.h + 50 or info[0] > self.w + 100:
                info[0] = random.randint(-100, self.w + 50)
                info[1] = random.randint(-200, -50)

            x = int(info[0])
            y = int(info[1])
            rotation = info[4]

            pr.draw_texture_ex(self.tall_pixel, pr.Vector2(x, y), rotation, self.scale, LIGHT_BLUE)

    def snow(self):
        for i in range(self.effect_count * 2):
            info = self.snow_info[i]

            info[1] += info[2]
            info[0] += info[2] * info[4]

            if info[1] > self.h + 50 or info[0] > self.w + 100 or info[0] < -100:
                info[0] = random.randint(-100, self.w + 50)
                info[1] = random.randint(-200, -50)

            x = int(info[0])
            y = int(info[1])
            scale = info[3]
            rotation = y * math.copysign(1, info[4])

            pr.draw_texture_ex(self.pixel, pr.Vector2(x, y), rotation, self.scale * scale, WHITE)

    def lava_pops(self):
        for i in range(self.effect_count // 2):
            info = self.lava_pops_info[i]

            info[0] += self.size * info[4]
            info[1] -= info[3] / 5

            info[3] -= self.size / 5

            if info[1] > self.h + self.size * 10:
                info[0] = random.randint(-50, self.w + 50)
                info[1] = random.randint(self.h + self.size, self.h + self.size * 4)
                info[3] = random.uniform(self.size, self.size * 10)

            x = int(info[0])
            y = int(info[1])
            scale = info[2]
            rotation = x * 5

            col = blend_colors(ORANGE, RED, abs(info[4]))

            pr.draw_texture_ex(self.pixel, pr.Vector2(x, y), rotation, self.scale * scale, col)

    def lengthdir_x(self, length, player_pos, target_pos):
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return 0

        return (dx / distance) * length

    def lengthdir_y(self, length, player_pos, target_pos):
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return 0

        return (dy / distance) * length

    def set_effects(self, biome="forest"):
        self.next_effects = self.biome_effects[biome]
