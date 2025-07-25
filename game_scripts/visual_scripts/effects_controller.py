import pyray as pr
from useful_draw_functions import *

import math, random


class VisualEffects:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.scale = 0
        self.current_effects = [""]
        self.next_effects = None

        self.size = h // 75

        image = pr.gen_image_color(self.size, self.size, WHITE)
        self.pixel = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.gen_image_color(int(self.size // 2), int(self.size * 3), WHITE)
        self.tall_pixel = pr.load_texture_from_image(image)
        pr.unload_image(image)

        self.max_effect_count = 30
        self.effect_count = self.max_effect_count

        # setu fireflies
        self.firefly_info = []
        for _ in range(self.max_effect_count):
            self.firefly_info.append([[random.randint(0, w), random.randint(0, h)], [random.randint(0, w), random.randint(0, h)],
                                      random.randint(30, 180), random.randrange(1, 2), random.random() * math.pi, random.random()])  # [x, y], target [x, y], decide different target, spd, glow, glow_offset

        self.rain_info = []
        for _ in range(self.max_effect_count * 2):  # More raindrops than fireflies
            self.rain_info.append([
                random.randint(-50, w + 50),  # x position
                random.randint(-200, h),  # y position
                random.uniform(self.size, self.size * 2) / 3,  # fall speed
                random.uniform(0.5, 1.2),  # scale multiplier
                random.uniform(-15, -25)  # rotation angle (negative for downward slant)
            ])  # [x, y, speed, scale, rotation]

        self.effects = {
            "fireflies": self.fireflies,
            "rain": self.rain
        }

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

            pr.draw_texture(self.pixel, x + int(val2), y, blend_colors(BLACK, YELLOW, val))

    def rain(self):
        for i in range(self.effect_count):
            info = self.rain_info[i]

            # Update position
            info[1] += info[2]  # y position falls based on speed
            info[0] += info[2] * 0.2  # slight horizontal drift

            # Reset raindrop when it goes off screen
            if info[1] > self.h + 50 or info[0] > self.w + 100:
                info[0] = random.randint(-100, self.w + 50)
                info[1] = random.randint(-200, -50)

            x = int(info[0])
            y = int(info[1])
            scale = info[3]
            rotation = info[4]

            pr.draw_texture_ex(self.tall_pixel, pr.Vector2(x, y), rotation, 1, LIGHT_BLUE)

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
