import cv2
from vision import screen_utils
from solver import ThaumSolver
from autoGUI.controls import ThaumGUIController
import time
from aspects import *
from hexgrid import HexCoord

time.sleep(3)
controller = ThaumGUIController()
controller.scan_screen()
# controller.place_aspect(SUPERBIA, HexCoord.from_axial(0, 0))
controller.place_hex_grid()

# img_path = r"C:\Users\Gleb\PycharmProjects\ThaumcraftSolver\test\1.png"
# img = cv2.imread(img_path)
# grid = screen_utils.scan_image(img)
# solver = ThaumSolver(grid)
# solver.solve()
# solver.print_grid()