import pyray as pr


WHITE = pr.Color(255, 255, 255, 255)
LIGHT_GRAY = pr.Color(200, 200, 200, 255)
LIGHTISH_GRAY = pr.Color(160, 160, 160, 255)
GRAY = pr.Color(128, 128, 128, 255)
DARK_GRAY = pr.Color(50, 50, 50, 255)
BLACK = pr.Color(0, 0, 0, 255)

YELLOW = pr.Color(220, 229, 94, 255)
DARKER_YELLOW = pr.Color(167, 173, 71, 255)
ORANGE = pr.Color(255, 128, 0, 255)

GREEN = pr.Color(0, 255, 0, 255)
RED = pr.Color(255,0,0,255)

SOFT_GREEN = pr.Color(153, 255, 153, 255)
SOFT_RED = pr.Color(255, 102, 102, 255)

LIGHT_BLUE = pr.Color(173, 216, 230, 255)
BLUE = pr.Color(0, 128, 255, 255)

SOFT_BROWN = pr.Color(183, 130, 95, 255)

PURPLE = pr.Color(168, 101, 201, 255)


def blend_colors(color1: pr.Color, color2: pr.Color, t: float) -> pr.Color:
    clamp = lambda x: max(0.0, min(1.0, x))  # Ensure t stays between 0 and 1
    t = clamp(t)

    r = int(color1.r + (color2.r - color1.r) * t)
    g = int(color1.g + (color2.g - color1.g) * t)
    b = int(color1.b + (color2.b - color1.b) * t)
    a = int(color1.a + (color2.a - color1.a) * t)

    return pr.Color(r, g, b, a)


def draw_fitted_text(font, text, x, y, max_width, initial_size, color, max_height=-1, align="left", center_y=False):
    size = initial_size
    text_metrics = pr.measure_text_ex(font, text, size, 0)
    text_width = text_metrics.x
    text_height = text_metrics.y

    while text_width > max_width and size > 1:
        size -= 1
        text_metrics = pr.measure_text_ex(font, text, size, 0)
        text_height = text_metrics.y
        text_width = text_metrics.x

    if max_height > 0:
        while text_height > max_height and size > 1:
            size -= 1
            text_metrics = pr.measure_text_ex(font, text, size, 0)
            text_height = text_metrics.y
            text_width = text_metrics.x

    if align == "right":
        x -= text_width

    if align == "center":
        x -= int(text_width // 2)

    if center_y:
        y -= text_metrics.y / 2

    pr.draw_text_pro(font, text, pr.Vector2(x, y), pr.Vector2(0, 0), 0, size, 0, color)


def get_coord_values(c):
    if isinstance(c[0][0], list):
        return c[0][0][0], c[0][1][0] - c[0][0][0], c[0][0][1], c[0][1][1] - c[0][0][1]
    return c[0][0], c[1][0] - c[0][0], c[0][1], c[1][1] - c[0][1]
