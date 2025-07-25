import pyray as pr
from window_stuff.window import Window
from window_bridge import UIBridge

import time

test_mode = True

ui = UIBridge(test_mode)

game_window = Window(ui, above_taskbar=True)
npc_manager = game_window.game.npc_manager

while not pr.window_should_close():
    ui_data = ui.receive()
    if ui_data:
        print(f"UI window sent: {ui_data}")
        if ui_data.get("close_window", 0) == 1:
            pr.close_window()
        if ui_data.get("add_npc", None):
            npc_manager.npcs.append(npc_manager.create_npc(npc_type=ui_data.get("add_npc")))

    game_window.main_step()

    # send all prepared data
    ui.send()

    #time.sleep(0.001)

# close also game_window
ui.prepare_to_send({"close_window": 1})
ui.send()

ui.close()
pr.close_window()
