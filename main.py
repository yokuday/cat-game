import pyray as pr
from window_stuff.window import Window

game_window = Window(above_taskbar=True)

while not pr.window_should_close():
    game_window.main_step()

pr.close_window()
