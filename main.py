import time

from autoGUI.controls import ThaumGUIController

time.sleep(3)
controller = ThaumGUIController()
controller.scan_screen()
controller.place_hex_grid()
while controller.inventory_scrolls_positions:
    controller.switch_scroll()
    controller.place_hex_grid()
