from collections import defaultdict

import cv2
import numpy as np
import pyautogui

from aspects import to_string, aspect_recipes
from vision import screen_utils
from hexgrid import HexGrid, HexCoord
import time
from custom_types import AspectType, Point
from .aspects_pages import aspects_pages
import solver


class ThaumGUIController:
    current_aspects_page: int
    left_aspect_button_pos: Point
    right_aspect_button_pos: Point
    aspects_position_grid: list[list[Point]]
    hex_grid: HexGrid
    hex_grid_center_pos: Point
    hex_size: float

    used_aspects_counter: dict[AspectType, int]

    def __init__(self):
        self.used_aspects_counter = defaultdict(int)

    def next_page(self):
        pyautogui.moveTo(*self.right_aspect_button_pos)
        time.sleep(0.1)
        pyautogui.click(
            clicks=5,
            interval=0.1,
        )
        self.current_aspects_page = min(self.current_aspects_page + 1, 2)

    def previous_page(self):
        pyautogui.moveTo(*self.left_aspect_button_pos)
        time.sleep(0.1)
        pyautogui.click(
            clicks=5 if self.current_aspects_page != 2 else 2,
            interval=0.1,
        )
        self.current_aspects_page = max(self.current_aspects_page - 1, 0)

    def turn_to_page(self, page: int):
        while self.current_aspects_page < page:
            self.next_page()
        while self.current_aspects_page > page:
            self.previous_page()

    def move_mouse_to_aspect(self, aspect: AspectType):
        # print("Moving to:", to_string(aspect))
        page, (row, col) = aspects_pages[aspect]
        self.turn_to_page(page)
        x, y = self.aspects_position_grid[row][col]
        pyautogui.moveTo(x, y)

    def place_aspect(self, aspect: AspectType, hex_coord: HexCoord):
        # print("Placing", to_string(aspect), "to", hex_coord)
        self.move_mouse_to_aspect(aspect)
        hex_x, hex_y = hex_coord.to_pixel(self.hex_size)
        hex_x += self.hex_grid_center_pos[0]
        hex_y += self.hex_grid_center_pos[1]
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(hex_x, hex_y, duration=0.2)
        pyautogui.mouseUp(button='left')

        self.used_aspects_counter[aspect] += 1
        if self.used_aspects_counter[aspect] >= 5:
            self.make_aspect(aspect, 5)

    def scan_screen(self):
        screen = np.array(pyautogui.screenshot())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        # screen = cv2.imread(r"C:\Users\Gleb\PycharmProjects\ThaumcraftSolver\test\1.png")

        self.left_aspect_button_pos, self.right_aspect_button_pos = screen_utils.get_aspects_page_buttons_position(
            screen)
        self.current_aspects_page = 0
        self.previous_page()
        self.previous_page()

        self.aspects_position_grid = screen_utils.get_aspects_positions(screen)

        self.hex_grid, self.hex_size, self.hex_grid_center_pos = screen_utils.scan_image(screen)

    def place_hex_grid(self) -> None:
        s = solver.ThaumSolver(self.hex_grid)
        s.solve()
        for hex_coord, value in self.hex_grid:
            if solver.is_aspect(value):
                self.place_aspect(value, hex_coord)
        s.print_grid()

    def make_aspect(self, aspect: AspectType, amount: int) -> None:
        if aspect_recipes[aspect]:  # aspect is not primal
            self.make_aspect(aspect_recipes[aspect][0], amount)
            self.make_aspect(aspect_recipes[aspect][1], amount)
            self.move_mouse_to_aspect(aspect)
            pyautogui.keyDown("shift")
            pyautogui.click(clicks=amount, interval=0.3)
            self.used_aspects_counter[aspect] -= amount
            pyautogui.keyUp("shift")
