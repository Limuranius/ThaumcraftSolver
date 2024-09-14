import cv2

from vision import screen_utils
from solver import ThaumSolver


img_path = r"C:\Users\Gleb\PycharmProjects\ThaumcraftSolver\test\1.png"
img = cv2.imread(img_path)
grid = screen_utils.scan_image(img)
solver = ThaumSolver(grid)
solver.solve()
solver.print_grid()