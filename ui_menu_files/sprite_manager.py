import pyray as pr


def load_sprite(file_path):
    return pr.load_texture(file_path)


def draw_sprite(texture, x, y, scale, origin="left", rot=0, tint=pr.Color(255, 255, 255, 255), xscale=1, frame_count=1, current_frame=0):
    w = texture.width
    h = texture.height

    fx = 0
    fy = 0

    if frame_count > 1:
        w = w // frame_count

    if current_frame > 0:
        fx += w * current_frame

    src_rec = pr.Rectangle(fx, fy, w * xscale, h)
    dst_rec = pr.Rectangle(x, y, w * scale, h * scale)

    orig = pr.Vector2(0, 0)

    if origin == "middle_center":
        orig = pr.Vector2(w * scale // 2, h * scale // 2)

    pr.draw_texture_pro(texture, src_rec, dst_rec, orig, rot, tint)
