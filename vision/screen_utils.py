import cv2
import numpy as np
import tqdm

from custom_types import Box, Point
from hexgrid import HexGrid, HexCoord
from paths import SCROLL_TEMPLATE_PATH
from . import hex_classifier


def crop_box(image: np.ndarray, box: Box) -> np.ndarray:
    x, y, w, h = box
    return image[y: y + h, x: x + w]


def get_minigame_area_box(img: np.ndarray) -> Box:
    low = np.array([0, 103, 93])
    high = np.array([180, 255, 255])
    threshold = cv2.inRange(img, low, high)

    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=lambda c: cv2.contourArea(c))
    x, y, w, h = cv2.boundingRect(max_contour)
    return x, y, w, h


def get_hex_image(
        img: np.ndarray,
        hex_coord: HexCoord,
        hex_size: float,
        center: Point
) -> np.ndarray:
    cx, cy = center
    x, y = hex_coord.to_pixel(hex_size)
    x += cx
    y += cy
    return img[y - hex_size: y + hex_size, x - hex_size: x + hex_size]


def scan_image(img: np.ndarray) -> [HexGrid, float, Point]:
    # Returns scanned grid, size of hex and coordinates of center hex
    result = HexGrid(4)
    minigame_box = get_minigame_area_box(img)
    img = crop_box(img, minigame_box)

    hex_size = get_hex_size(img)
    h, w = img.shape[:2]
    cx = w // 2
    cy = h // 2

    minigame_x, minigame_y = minigame_box[:2]

    for hex_coord, _ in tqdm.tqdm(result):
        hex_img = get_hex_image(img, hex_coord, hex_size, (cx, cy))
        aspect = hex_classifier.classify_hex(hex_img)
        result.set_data(hex_coord, aspect)
    return result, hex_size, (cx + minigame_x, cy + minigame_y)


def get_hex_size(minigame_img: np.ndarray) -> int:
    h, w = minigame_img.shape[:2]
    hex_size = h / 8.1 / 2
    hex_size = int(hex_size)
    return hex_size



def get_thaum_gui_box(image: np.ndarray) -> Box:
    x, y, w, h = get_minigame_area_box(image)
    x -= w * 0.6
    w += w * 0.6
    x = int(x)
    w = int(w)
    return x, y, w, h


def get_aspects_page_buttons_position(image: np.ndarray) -> tuple[Point, Point]:
    x, y, w, h = get_thaum_gui_box(image)
    x1, y1 = x + 0.15 * w, y + h * 0.79
    x2, y2 = x + 0.25 * w, y1
    x1, y1 = int(x1), int(y1)
    x2, y2 = int(x2), int(y2)
    return (x1, y1), (x2, y2)


def get_aspects_positions(image: np.ndarray) -> list[list[Point]]:
    x, y, w, h = get_thaum_gui_box(image)
    left_margin = w * 0.05
    up_margin = h * 0.27
    step = h * 0.11
    positions = [[None for _ in range(5)] for __ in range(5)]
    for i in range(5):
        for j in range(5):
            positions[i][j] = (
                int(x + left_margin + j * step),
                int(y + up_margin + i * step)
            )
    return positions


def draw_box(img, box):
    x, y, w, h = box
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)


def draw_point(img, point):
    x, y = point
    cv2.circle(img, (x, y), 3, (255, 0, 0), -1)


def images_difference(img1, img2):
    img1 = img1.astype(int)
    img2 = img2.astype(int)
    diff = np.abs(img1 - img2).astype(np.uint8)
    return diff


def get_inventory_boxes(img: np.ndarray) -> list[Box]:
    mask = cv2.inRange(img, np.array([198, 198, 198]), np.array([202, 202, 202]))
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = list(contours)
    contours.sort(key=cv2.contourArea, reverse=True)
    outer_contour, inner_bigger_contour, inner_smaller_contour = contours[:3]
    inner_bigger_box = cv2.boundingRect(inner_bigger_contour)
    inner_smaller_box = cv2.boundingRect(inner_smaller_contour)

    boxes = []
    width = inner_bigger_box[2] // 9
    height = inner_bigger_box[3] // 3
    for i in range(3):
        for j in range(9):
            boxes.append((
                inner_bigger_box[0] + j * width,
                inner_bigger_box[1] + i * height,
                width,
                height
            ))
    for j in range(9):
        boxes.append((
            inner_smaller_box[0] + j * width,
            inner_smaller_box[1],
            width,
            height
        ))
    return boxes


def find_scrolls_positions(img: np.ndarray) -> list[Point]:
    boxes = get_inventory_boxes(img)
    scroll_img = cv2.imread(SCROLL_TEMPLATE_PATH)
    result = []
    for box in boxes:
        box_img = crop_box(img, box)
        box_img = cv2.resize(box_img, (scroll_img.shape[:2]))
        diff = images_difference(box_img, scroll_img)
        score = diff.mean() / 255
        if score <= 0.1:
            result.append((
                box[0] + box[2] // 2,
                box[1] + box[3] // 2,
            ))
    return result


def find_current_scroll_position(img: np.ndarray) -> Point:
    x, y, w, h = get_thaum_gui_box(img)
    return int(x + w * 0.3), int(y + h * 0.05)
