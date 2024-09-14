import cv2
import numpy as np
from hexgrid import HexGrid, HexCoord
from math import sqrt
from . import hex_classifier
import tqdm

grid = HexGrid(3)


def flat_hex_to_pixel(coords: HexCoord, size: float):
    q, r = coords.axial
    x = size * (3 / 2 * q)
    y = size * (sqrt(3) / 2 * q + sqrt(3) * r)
    return int(x), int(y)


def retrieve_minigame_area(img: np.ndarray) -> np.ndarray:
    low = np.array([0, 103, 93])
    high = np.array([180, 255, 255])
    threshold = cv2.inRange(img, low, high)

    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=lambda c: cv2.contourArea(c))
    x, y, w, h = cv2.boundingRect(max_contour)
    return img[y: y + h, x: x + w]


def draw_hexes(minigame_area_img: np.ndarray) -> np.ndarray:
    h, w = minigame_area_img.shape[:2]
    # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cx = w // 2
    cy = h // 2
    hex_size = h / 8.1 / 2
    circle_radius = int(hex_size * 0.85)
    for hex_coord, _ in grid:
        x, y = flat_hex_to_pixel(hex_coord, hex_size)
        cv2.circle(img, (cx + x, cy + y), circle_radius, (255, 0, 0), 2)
    return img





def get_hex_image(img: np.ndarray, hex_coord: HexCoord) -> np.ndarray:
    h, w = img.shape[:2]
    cx = w // 2
    cy = h // 2
    hex_size = h / 8.1 / 2
    x, y = flat_hex_to_pixel(hex_coord, hex_size)
    hex_size = int(hex_size)
    x += cx
    y += cy
    return img[y - hex_size: y + hex_size, x - hex_size: x + hex_size]


def check_hex_values(minigame_area_img: np.ndarray):
    gray = cv2.cvtColor(minigame_area_img, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 80, 150)
    h, w = minigame_area_img.shape[:2]
    cx = w // 2
    cy = h // 2
    hex_size = h / 8.1 / 2
    circle_radius = int(hex_size * 0.85)
    for hex_coord, _ in grid:
        hex_img = get_hex_image(minigame_area_img, hex_coord)
        print("Class:", hex_classifier.classify_hex(hex_img))
        # x, y = flat_hex_to_pixel(hex_coord, hex_size)
        # hex_mask = hex_classifier.get_circle_mask(minigame_area_img, x + cx, y + cy, circle_radius)
        # masked = cv2.bitwise_and(hex_mask, canny)
        # print(masked.sum() // 255)
        # cv2.imshow("canny", get_hex_image(canny, hex_coord))
        cv2.imshow("", hex_img)
        # cv2.imshow("canny", masked)
        cv2.waitKey(0)


def scan_image(img: np.ndarray) -> HexGrid:
    result = HexGrid(4)
    img = retrieve_minigame_area(img)

    for hex_coord, _ in tqdm.tqdm(result):
        hex_img = get_hex_image(img, hex_coord)
        aspect = hex_classifier.classify_hex(hex_img)
        result.set_data(hex_coord, aspect)
    return result

