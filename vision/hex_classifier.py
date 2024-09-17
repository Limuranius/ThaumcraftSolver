import numpy as np
import cv2
from . import sprite_reader
from aspects import *
from hexgrid.HexGrid import WALL, FREE

sprites_histograms = dict()
for aspect in aspects_list:
    sprite_img = sprite_reader.get_aspect_sprite(aspect)
    hist_img = cv2.calcHist(
        [sprite_img],
        [0, 1, 2],
        None,
        [256, 256, 256],
        [0, 256, 0, 256, 0, 256]
    )
    cv2.normalize(hist_img, hist_img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    sprites_histograms[aspect] = hist_img


def classify_hex(hex_img: np.ndarray) -> int:
    hex_img = fit_size(hex_img, 50, 50)

    ring_score = get_ring_score(hex_img)
    inner_circle_score = get_inner_circle_score(hex_img)

    if inner_circle_score < 100:
        if ring_score > 400:
            return FREE
        else:
            return WALL
    else:
        differences = []
        hex_hist = cv2.calcHist(
            [hex_img],
            [0, 1, 2],
            None,
            [256, 256, 256],
            [0, 256, 0, 256, 0, 256]
        )
        cv2.normalize(hex_hist, hex_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        for aspect in aspects_list:
            sprite_hist = sprites_histograms[aspect]
            score = cv2.compareHist(sprite_hist, hex_hist, cv2.HISTCMP_CORREL)
            differences.append((aspect, score))
        max_aspect, max_score = max(differences, key=lambda x: x[1])
        differences.sort(key=lambda x: x[1], reverse=True)
        return max_aspect


def fit_size(img, h, w):
    size = img.shape[:2]
    f = min(h / size[0], w / size[1])
    return cv2.resize(img, (int(size[1] * f), int(size[0] * f)), interpolation=cv2.INTER_AREA)


def get_ring_score(hex_img):
    gray = cv2.cvtColor(hex_img, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 70, 125)

    kernel = np.ones((3, 3), 'uint8')
    canny = cv2.dilate(canny, kernel, iterations=1)

    h, w = hex_img.shape[:2]
    circle_radius = int(w / 2 * 0.75)
    circle_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(circle_mask, (w // 2, h // 2), circle_radius, 255, 3)

    masked = cv2.bitwise_and(circle_mask, canny)

    ring_score = masked.sum() // 255
    return ring_score


def get_inner_circle_score(hex_img):
    hsv = cv2.cvtColor(hex_img, cv2.COLOR_BGR2HSV)
    low = np.array([0, 102, 144])
    high = np.array([21, 255, 255])
    threshold = cv2.inRange(hsv, low, high)
    threshold = cv2.bitwise_not(threshold)

    h, w = hex_img.shape[:2]
    circle_radius = int(w / 2 * 0.7)
    circle_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(circle_mask, (w // 2, h // 2), circle_radius, 255, -1)

    masked = cv2.bitwise_and(circle_mask, threshold)

    inner_circle_score = masked.sum() // 255

    return inner_circle_score


def hist_difference(img1: np.ndarray, img2: np.ndarray):
    hist_img1 = cv2.calcHist([img1], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist_img1, hist_img1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    hist_img2 = cv2.calcHist([img2], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist_img2, hist_img2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    metric_val = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_CORREL)
    return metric_val
