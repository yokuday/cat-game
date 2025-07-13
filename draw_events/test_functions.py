import pyray as pr


class Functions:
    def __init__(self, w, h):
        self.width = w
        self.height = h

    def draw_objects(self):
        pr.draw_rectangle(100, 100, 200, 150, pr.Color(255, 0, 0, 29))
        pr.draw_circle(500, 300, 80, pr.Color(0, 255, 0, 255))

    def draw_fps(self):
        fps = pr.get_fps()
        frame_time = pr.get_frame_time() * 1000  # Convert to ms
        pr.draw_text(f"FPS: {fps}", 10, 10, 20, pr.Color(255, 255, 255, 200))
        pr.draw_text(f"Frame: {frame_time:.1f}ms", 10, 35, 20, pr.Color(255, 255, 255, 200))
