import uuid

import pyray as pr

from useful_draw_functions import *

import math, random


class VisualEffects:
    def __init__(self, w, h, player_info, y_offset, game):
        self.w = w
        self.h = h

        self.game = game

        self.player_info = player_info

        self.scale = 0
        self.current_effects = [""]
        self.next_effects = None

        self.size = max(int(h // 75), 1)
        self.big_size = max(int(h // 15), 1)

        image = pr.gen_image_color(self.size, self.size, WHITE)
        self.pixel = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.gen_image_color(max(int(self.size // 2), 1), int(self.size * 3), WHITE)
        self.tall_pixel = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.gen_image_color(self.big_size, self.big_size, WHITE)
        self.big_pixel = pr.load_texture_from_image(image)
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

        # waves
        self.waves = Waves(self.w, self.h, player_info, y_offset, self)

        # fog
        self.fog = RainStorm(self.w, self.h, self.game)

        # sunshine
        self.sunshine = SunshineEffect(self.w, self.h, self)

        self.effects = {
            "fireflies": self.fireflies,
            "rain": self.rain,
            "snow": self.snow,
            "lava pops": self.lava_pops,
            "waves": self.waves.step,
            "fog": self.fog.step,
            "sunshine": self.sunshine.step
        }

        self.before_step = ["waves"]

        self.biome_effects = {
            "forest": ["", "rain"],
            "fall_forest": [""],
            "spring_forest": [""],
            "pine_forest": [""],
            "beach": ["waves"],
            "swamp": [""]
        }

        # temporary effects
        self.tmp_effects = {}
            #(pos, timer, effect)

        # set initial effect for biome
        self.set_effects(self.player_info.info["current_biome"])

        self.variable_pi = 0

    def step(self, before_step=False):
        delta_time = pr.get_frame_time() * 60

        if not before_step:
            self.variable_pi += 1 / 1000 * delta_time
            if self.variable_pi >= 2 * math.pi:
                self.variable_pi -= 2 * math.pi

            if self.next_effects:
                if self.scale > 0:
                    self.scale = max(self.scale - 1 / 15, 0)
                else:
                    self.current_effects = self.next_effects
                    self.next_effects = None

                    # RESET WHITEOUT
                    self.game.whiteness = 0
                    self.game.white_mode = False
            else:
                self.scale = min(self.scale + 1 / 15, 1)

            # draw visual effects
            if self.scale > 0:
                for effect in self.current_effects:
                    if self.effects.get(effect):
                        if effect not in self.before_step:
                            self.effects[effect]()

            # visual dynamic temporary effects
            for uuid in list(self.tmp_effects.keys()):
                effect = self.tmp_effects[uuid]

                effect[1] -= 1 / effect[3] * delta_time

                effect[2](effect[0], effect[1])

                if effect[1] <= 0:
                    self.tmp_effects.pop(uuid)
        else:
            # draw BEFORE visual effects
            if self.scale > 0:
                for effect in self.current_effects:
                    if self.effects.get(effect):
                        if effect in self.before_step:
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

    def add_effect(self, pos, effect="smoke_particle"):
        particles = {
            "smoke_particle": [self.smoke_particle, 50],
            "falling_leaves": [self.tree_leaves_particle, 80]
        }

        self.tmp_effects[uuid.uuid4()] = [pos, 1, particles[effect][0], particles[effect][1]]

    def smoke_particle(self, pos, scale, rotation=0):
        x, y = pos[0], pos[1]
        progress = 1.0 - scale
        alpha = 1.0 if progress <= 0.2 else 1.0 - ((progress - 0.2) / 0.8)

        alpha /= 1.5

        expansion = self.big_pixel.width * 2 + self.big_pixel.width * 3 * (1.0 - pow(1.0 - progress, 3))
        particle_size = min(1.3 - progress, 1) * scale * 2

        for i in range(20):
            angle = (i / 20) * 3.28318 + rotation * progress * 2
            wave = math.sin(angle * 3 + progress * 4) * 0.3 + math.sin(angle * 7 - progress * 2) * 0.15
            radius = expansion * (1.0 + wave * 0.3) * math.cos(x + i)
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius - progress * 10

            dif_size = 0.5 + abs(math.cos(x + i * 2 + 2))

            pr.draw_texture_ex(self.big_pixel, pr.Vector2(px, py), angle, particle_size * dif_size, WHITE)

    def tree_leaves_particle(self, pos, scale, rotation=0):
        x, y = pos[0], pos[1]
        progress = 1.0 - scale
        random_seed = math.sin(x * 0.1) * 1000
        num_leaves = 8

        for i in range(num_leaves):
            leaf_random = math.sin(random_seed + i * 7.3) * 0.5 + 0.5
            leaf_random2 = math.cos(random_seed + i * 13.7) * 0.5 + 0.5

            start_angle = leaf_random * math.pi * 2
            start_radius = leaf_random2 * self.big_pixel.width * 4.5

            start_x = x + math.cos(start_angle) * start_radius
            start_y = y + math.sin(start_angle) * start_radius

            fall_y = progress * 120 + math.sin(progress * 2 + i) * 5
            sway_x = math.sin(progress * 1.5 + i * 3) * 15 * (1 + progress)

            px = start_x + sway_x
            py = start_y + fall_y

            if progress > 0.7:
                alpha = 1.0 - ((progress - 0.7) / 0.3)
            else:
                alpha = 0.8

            particle_size = 0.3
            leaf_rotation = fall_y * 3

            colors = {
                "forest": SOFT_GREEN,
                "fall_forest": ORANGE
            }

            leaf_color = pr.fade(colors.get(self.player_info.info["current_biome"], SOFT_GREEN), alpha)

            pr.draw_texture_ex(
                self.big_pixel,
                pr.Vector2(px, py),
                leaf_rotation,
                particle_size,
                leaf_color
            )


class Waves:
    class Ripple:
        def __init__(self):
            self.x = 0
            self.strength = 0
            self.time = 0

    def __init__(self, w, h, player_info, y_offset, parent):
        self.WATER_SEGMENTS = w // 10
        self.WATER_WIDTH = w
        self.WATER_HEIGHT = 100
        self.WATER_Y = h + y_offset // 2
        self.y_offset = y_offset

        self.player_info = player_info

        self.parent = parent

        self.ripples = [self.Ripple() for _ in range(8)]

    def step(self):
        current_biome = self.parent.player_info.info["current_biome"]

        dt = pr.get_frame_time()
        current_time = pr.get_time() * 2

        colors = {
            "beach": pr.Color(28, 107, 160, 255),
            "forest": pr.Color(92, 179, 255, 255),
            "pine_forest": pr.Color(14, 90, 156, 255),
            "fall_forest": pr.Color(92, 179, 255, 255),
            "spring_forest": pr.Color(92, 179, 255, 255),
            "swamp": pr.Color(92, 179, 255, 255)
        }

        # Update ripples
        for r in self.ripples:
            if r.strength > 0.01:
                r.time += dt * 5 * 1.25  # Speed of ripple expansion
                r.strength *= 0.95  # Decay rate
                if r.time > 10.0:
                    r.strength = 0

        # Add ripple on click
        if pr.is_mouse_button_pressed(0):
            self.add_ripple(pr.get_mouse_x(), 1)

        # Draw water surface with waves
        points = []
        for i in range(self.WATER_SEGMENTS + 1):
            x = i * (self.WATER_WIDTH / self.WATER_SEGMENTS)
            y = self.WATER_Y - self.y_offset * 2 * (1 - self.parent.scale)

            # Base wave
            y += math.sin(x * 0.02 + current_time * 2 * 2) * self.y_offset / 5
            y += math.sin(x * 0.01 + current_time * 1.5 * 2) * self.y_offset / 6

            # Ripple contributions
            for r in self.ripples:
                if r.strength > 0.01:
                    dist = abs(x - r.x)
                    if dist < r.time * 50:  # Ripple radius
                        decay = r.strength * math.exp(-dist * 0.01)
                        y += math.sin(dist * 0.1 - r.time * 5) * decay * 20

            points.append((x, y))

        # Draw water as filled polygon
        for i in range(len(points) - 1):
            # Draw water body (filled)
            pr.draw_rectangle(int(points[i][0]), int(points[i][1]),
                              int((self.WATER_WIDTH / self.WATER_SEGMENTS)),
                              (100 + int(points[i][1])),
                              colors[current_biome])

            # Draw water surface line
            pr.draw_line_ex(pr.Vector2(int(points[i][0]), int(points[i][1])),
                            pr.Vector2(int(points[i + 1][0]), int(points[i + 1][1])),
                            abs(self.y_offset) // 10, WHITE)

    def add_ripple(self, x_pos, strength=1.0):
        for r in self.ripples:
            if r.strength < 0.01:
                r.x = x_pos
                r.strength = strength
                r.time = 0
                break


class RainStorm:
    def __init__(self, w, h, game):
        self.width, self.height = w, h
        self.rain_drops = [
            [random.randint(0, w), random.randint(-h, 0), random.uniform(15, 25), random.uniform(0.5, 1.5)] for _ in
            range(200)]
        self.lightning_time = 0
        self.lightning_flash = 0
        self.next_lightning = random.uniform(2, 5)
        self.lightning_branches = []
        self.lightning_glow = 0
        self.strike_x = 0
        self.strike_progress = 0

        self.game = game

    def generate_lightning(self, x, y, end_y, angle=math.pi / 2, depth=0, main=True):
        if y >= end_y or depth > 4: return
        segments = []
        while y < end_y:
            next_y = y + random.randint(20, 50)
            offset = random.randint(-40, 40) if not main else random.randint(-20, 20)
            next_x = x + offset
            segments.append((x, y, next_x, next_y, max(1, 8 - depth * 2) if main else max(1, 5 - depth)))
            if random.random() < (0.4 if main else 0.2) and depth < 3:
                branch_angle = angle + random.uniform(-math.pi / 3, math.pi / 3)
                self.generate_lightning(next_x, next_y, end_y + random.randint(-50, 50), branch_angle, depth + 1, False)
            x, y = next_x, next_y
        self.lightning_branches.extend(segments)

    def step(self):
        dt = pr.get_frame_time()
        self.lightning_time += dt

        for drop in self.rain_drops:
            drop[1] += drop[2] * self.height / 4 * dt * drop[3]
            drop[0] += drop[2] * self.height / 20 * dt
            if drop[1] > self.height: drop[1] = random.randint(-100, -10); drop[0] = random.randint(-50, self.width)

        if self.lightning_time > self.next_lightning:
            self.lightning_flash = 1.0
            self.lightning_glow = 1.5
            self.strike_progress = 0
            self.lightning_branches = []
            self.strike_x = random.randint(self.width // 4, 3 * self.width // 4)
            self.generate_lightning(self.strike_x, -20, self.height * 0.9)
            for _ in range(random.randint(1, 3)):
                self.generate_lightning(self.strike_x + random.randint(-100, 100), random.randint(0, 100),
                                        self.height * 0.7, depth=1, main=False)
            self.lightning_time = 0
            self.next_lightning = random.uniform(2, 8)

        if self.lightning_glow > 0:
            self.game.white_mode = True
            self.game.whiteness = self.lightning_glow

            # pr.draw_rectangle(0, 0, self.width, self.height,
            #                   pr.Color(255, 255, 255, int(min(self.lightning_glow * 150, 255))))
            self.lightning_glow -= dt * 2
        else:
            self.game.white_mode = False

        if self.lightning_flash > 0:
            self.strike_progress = min(1.0, self.strike_progress + dt * 12)
            pulse = 1 + math.sin(self.lightning_flash * 30) * 0.3
            max_y = self.height * 0.9 * self.strike_progress

            for x1, y1, x2, y2, thickness in self.lightning_branches:
                if y1 < max_y and y2 < max_y:
                    for j in range(3):
                        glow_thick = thickness * (4 - j) * pulse
                        alpha = int(self.lightning_flash * (80 - j * 20))
                        pr.draw_line_ex(pr.Vector2(x1, y1), pr.Vector2(x2, min(y2, max_y)), glow_thick,
                                        pr.Color(220, 220, 255, alpha))
                    pr.draw_line_ex(pr.Vector2(x1, y1), pr.Vector2(x2, min(y2, max_y)), thickness * pulse * 1.5,
                                    pr.WHITE)

            if self.strike_progress > 0.8:
                pr.draw_circle_gradient(self.strike_x, int(max_y), int(200 * self.lightning_flash * pulse),
                                        pr.Color(255, 255, 255, int(self.lightning_flash * 100)),
                                        pr.Color(200, 200, 255, 0))

            self.lightning_flash -= dt * 1.5

        for drop in self.rain_drops:
            pr.draw_line_ex(pr.Vector2(drop[0], drop[1]), pr.Vector2(drop[0] - self.width / 500, drop[1] - drop[2]), 1 + drop[3],
                            pr.Color(150, 160, 200, 180))
            if random.random() < 0.001: pr.draw_circle(int(drop[0]), int(self.height - 5), random.randint(2, 4),
                                                       pr.Color(150, 160, 200, 50))


class SunshineEffect:
    def __init__(self, w, h, parent):
        self.parent = parent

        self.width, self.height = w, h
        self.time = 0
        self.rays = []
        for i in range(10):
            x = random.randint(0, w)
            while any(abs(x - r['x']) < w / 30 for r in self.rays):
                x = random.randint(0, w)
            self.rays.append({
                'x': x,
                'strength': random.uniform(0.3, 1.0),
                'fade_offset': random.uniform(0, math.pi * 2),
                'width': random.uniform(0.5, 0.8),
            })

    def step(self):
        dt = pr.get_frame_time()
        self.time += dt

        for ray in self.rays:
            fade = abs(math.sin(self.time * 0.15 + ray['fade_offset']) + 1)
            strength = ray['strength'] * fade

            width_change = 1
            if strength < 0.80:
                width_change = max(0, (strength - 0.65) / 0.15)

            if strength <= 0.65:
                new_x = random.randint(0, self.width)
                while any(abs(new_x - r['x']) < self.width / 30 for r in self.rays if r != ray):
                    new_x = random.randint(0, self.width)
                ray['x'] = new_x
                ray['width'] = random.uniform(0.5, 0.8)
                ray['strength'] = random.uniform(0.3, 1.0)

            start_x = ray['x']
            end_x = ray['x'] + self.width / 10
            start_y = -self.height / 5
            end_y = self.height * 1.2

            alpha = min(max(int(255 * strength * 0.25), 5), 255)

            pr.draw_line_ex(pr.Vector2(start_x, start_y), pr.Vector2(end_x, end_y),
                            int(self.width / 40 * ray['width'] * width_change * self.parent.scale),
                            pr.Color(168, 168, 64, alpha))
