import time
from collections import defaultdict

import cv2
import numpy as np
import pyautogui

import config
import solver
from aspects import aspect_recipes, aspects_list
from custom_types import AspectType, Point
from hexgrid import HexGrid, HexCoord
from vision import screen_utils
from .aspects_pages import aspects_pages


class ThaumGUIController:
    current_aspects_page: int
    left_aspect_button_pos: Point
    right_aspect_button_pos: Point
    aspects_position_grid: list[list[Point]]
    hex_grid: HexGrid
    hex_grid_center_pos: Point
    hex_size: float

    aspects_left_counter: dict[AspectType, int]

    current_scroll_pos: Point
    inventory_scrolls_positions: list[Point]

    def __init__(self):
        self.aspects_left_counter = defaultdict(int)

    def next_page(self):
        pyautogui.moveTo(*self.right_aspect_button_pos)
        pyautogui.click(
            clicks=5,
            interval=config.PAGE_BUTTON_CLICK_INTERVAL,
        )
        self.current_aspects_page = min(self.current_aspects_page + 1, 2)

    def previous_page(self):
        pyautogui.moveTo(*self.left_aspect_button_pos)
        pyautogui.click(
            clicks=5 if self.current_aspects_page != 2 else 2,
            interval=config.PAGE_BUTTON_CLICK_INTERVAL,
        )
        self.current_aspects_page = max(self.current_aspects_page - 1, 0)

    def turn_to_page(self, page: int):
        while self.current_aspects_page < page:
            self.next_page()
        while self.current_aspects_page > page:
            self.previous_page()

    def move_mouse_to_aspect(self, aspect: AspectType):
        page, (row, col) = aspects_pages[aspect]
        self.turn_to_page(page)
        x, y = self.aspects_position_grid[row][col]
        pyautogui.moveTo(x, y)

    def place_aspect(self, aspect: AspectType, hex_coord: HexCoord):
        if self.aspects_left_counter[aspect] == 0:
            self.craft_aspect(aspect, config.CRAFT_ASPECTS_AMOUNT)
        self.aspects_left_counter[aspect] -= 1

        self.move_mouse_to_aspect(aspect)
        hex_x, hex_y = hex_coord.to_pixel(self.hex_size)
        hex_x += self.hex_grid_center_pos[0]
        hex_y += self.hex_grid_center_pos[1]
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(hex_x, hex_y, duration=config.ASPECT_DRAG_DURATION)
        pyautogui.mouseUp(button='left')

    def scan_screen(self):
        screen = np.array(pyautogui.screenshot())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        self.left_aspect_button_pos, self.right_aspect_button_pos = screen_utils.get_aspects_page_buttons_position(
            screen)
        self.current_aspects_page = 0
        self.previous_page()
        self.previous_page()

        self.aspects_position_grid = screen_utils.get_aspects_positions(screen)

        self.update_hex_grid(screen)

        self.current_scroll_pos = screen_utils.find_current_scroll_position(screen)
        self.inventory_scrolls_positions = screen_utils.find_scrolls_positions(screen)
        print("Scrolls count:", len(self.inventory_scrolls_positions))

    def place_hex_grid(self) -> None:
        s = solver.ThaumSolver(self.hex_grid)
        initial_aspects = s.find_aspects_coords()
        s.solve()
        for hex_coord, value in self.hex_grid:
            if solver.is_aspect(value) and hex_coord not in initial_aspects:
                self.place_aspect(value, hex_coord)
        s.print_grid()

    def craft_aspect(self, aspect: AspectType, amount: int) -> None:
        if aspect_recipes[aspect]:  # aspect is not primal
            self.craft_aspect(aspect_recipes[aspect][0], amount)
            self.craft_aspect(aspect_recipes[aspect][1], amount)
            self.move_mouse_to_aspect(aspect)
            pyautogui.keyDown("shift")
            pyautogui.click(clicks=amount, interval=config.MAKE_ASPECT_CLICK_INTERVAL)
            self.aspects_left_counter[aspect] += amount
            child1, child2 = aspect_recipes[aspect]
            self.aspects_left_counter[child1] -= amount
            self.aspects_left_counter[child2] -= amount
            pyautogui.keyUp("shift")

    def update_hex_grid(self, image: np.ndarray):
        self.hex_grid, self.hex_size, self.hex_grid_center_pos = screen_utils.scan_image(image)

    def switch_scroll(self):
        pyautogui.keyDown("shift")
        pyautogui.moveTo(*self.current_scroll_pos)
        pyautogui.click()
        if self.inventory_scrolls_positions:
            pyautogui.moveTo(self.inventory_scrolls_positions.pop())
            pyautogui.click()
        pyautogui.keyUp("shift")
        time.sleep(0.5)
        screen = np.array(pyautogui.screenshot())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        self.update_hex_grid(np.array(screen))

    def craft_all_aspects(self, amount: int):
        for aspect in aspects_list:
            self.craft_aspect(aspect, amount)
