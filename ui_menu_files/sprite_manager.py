import pyray as pr


def load_sprite(file_path):
    return pr.load_texture(file_path)


def draw_sprite(texture, x, y, scale, origin="left", rot=0, tint=pr.Color(255, 255, 255, 255)):
    w = texture.width
    h = texture.height

    src_rec = pr.Rectangle(0, 0, w, h)
    dst_rec = pr.Rectangle(x, y, w * scale, h * scale)

    orig = pr.Vector2(0, 0)

    if origin == "middle_center":
        orig = pr.Vector2(w * scale // 2, h * scale // 2)

    pr.draw_texture_pro(texture, src_rec, dst_rec, orig, rot, tint)
