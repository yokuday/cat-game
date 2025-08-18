import pyray as pr
from window_stuff.window import Window
from window_bridge import UIBridge

import time

test_mode = True
# pyinstaller --onefile --windowed main.py

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
            npc_manager.npcs.insert(0, npc_manager.create_npc(npc_type=ui_data.get("add_npc")))
        if ui_data.get("remove_npc", None):
            for i, npc in enumerate(npc_manager.npcs):
                if npc["type"] == ui_data.get("remove_npc"):
                    game_window.player_info.next_biome = ui_data.get("current_biome", game_window.player_info.info["current_biome"])  # reset the field
                    npc_manager.npcs.pop(i)
                    break
        if ui_data.get("current_biome", None):
            if (ui_data.get("current_biome", "forest") != game_window.player_info.info["current_biome"] or
                    (game_window.player_info.next_biome is not None and game_window.player_info.next_biome != ui_data.get("current_biome", "forest"))):
                game_window.player_info.next_biome = ui_data.get("current_biome", "forest")  # change biome
                game_window.game.effects.set_effects(ui_data.get("current_biome", "forest"))  # reset effects
        if ui_data.get("change_settings", None):
            pass
        if ui_data.get("minimize_ui", None):
            game_window.game.ui.arrow_clicked = False
            ui.prepare_to_send({"show_window": False})

    game_window.main_step()
    npc_manager = game_window.game.npc_manager  # reasign, in case new npc_manager was created

    # send all prepared data
    ui.send()

    #time.sleep(0.001)

# close also game_window
ui.prepare_to_send({"close_window": 1})
ui.send()

ui.close()
pr.close_window()
