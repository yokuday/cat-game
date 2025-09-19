import pyray as pr
import math
from pyray import ffi

# Water configuration
WATER_SEGMENTS = 200
WATER_WIDTH = 800
WATER_HEIGHT = 200
WATER_Y = 400  # Y position on screen


# Ripple system
class Ripple:
    def __init__(self):
        self.x = 0
        self.strength = 0
        self.time = 0


ripples = [Ripple() for _ in range(8)]

# Initialize
pr.init_window(800, 600, "Water Waves")
pr.set_target_fps(60)


def add_ripple(x_pos, strength=1.0):
    """Add a new ripple at the given x position"""
    for r in ripples:
        if r.strength < 0.01:
            r.x = x_pos
            r.strength = strength
            r.time = 0
            break


# Main loop
while not pr.window_should_close():
    dt = pr.get_frame_time()
    current_time = pr.get_time() * 1.5

    # Update ripples
    for r in ripples:
        if r.strength > 0.01:
            r.time += dt * 5 * 1.25  # Speed of ripple expansion
            r.strength *= 0.95  # Decay rate
            if r.time > 10.0:
                r.strength = 0

    # Add ripple on click
    if pr.is_mouse_button_pressed(0):
        add_ripple(pr.get_mouse_x(), 1)

    # Draw
    pr.begin_drawing()
    pr.clear_background(pr.SKYBLUE)

    # Draw water surface with waves
    points = []
    for i in range(WATER_SEGMENTS + 1):
        x = i * (WATER_WIDTH / WATER_SEGMENTS)
        y = WATER_Y

        # Base wave
        y += math.sin(x * 0.02 + current_time * 2) * 5 * 1.5
        y += math.sin(x * 0.01 + current_time * 1.5) * 8 * 1.5

        # Ripple contributions
        for r in ripples:
            if r.strength > 0.01:
                dist = abs(x - r.x)
                if dist < r.time * 50:  # Ripple radius
                    decay = r.strength * math.exp(-dist * 0.01)
                    y += math.sin(dist * 0.1 - r.time * 5) * decay * 20

        points.append((x, y))

    # Draw water as filled polygon
    for i in range(len(points) - 1):
        # Draw water surface line
        pr.draw_line(int(points[i][0]), int(points[i][1]),
                     int(points[i + 1][0]), int(points[i + 1][1]),
                     pr.DARKBLUE)

        # Draw water body (filled)
        pr.draw_rectangle(int(points[i][0]), int(points[i][1]),
                          int((WATER_WIDTH / WATER_SEGMENTS)),
                          600 - int(points[i][1]),
                          pr.Color(28, 107, 160, 180))

    pr.draw_text("Click to add ripples", 10, 10, 20, pr.BLACK)
    pr.end_drawing()

pr.close_window()