import pyray as pr
from window_stuff.window import Window
from window_bridge import UIBridge

ui = UIBridge()

game_window = Window(ui, above_taskbar=True)

while not pr.window_should_close():
    # ui_data = ui.receive()
    # if ui_data:
    #     print(f"UI window sent: {ui_data}")

    game_window.main_step()

# close also game_window
ui.send({"close_window": 1})

ui.close()
pr.close_window()
