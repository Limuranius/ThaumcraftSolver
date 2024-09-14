import cv2
import numpy as np
from aspects import *
from custom_types import AspectType

spritesheet_path = r"C:\Users\Gleb\PycharmProjects\ThaumcraftSolver\vision\T4aspects.png"
spritesheet = cv2.imread(spritesheet_path)
spritesheet_alpha = cv2.imread(spritesheet_path, cv2.IMREAD_UNCHANGED)[:, :, 3]

SIZE = 32


def get_aspect_sprite(aspect: AspectType) -> np.ndarray:
    index = aspect_to_sprite_index[aspect]
    row = index // 16
    col = index % 16
    sprite = spritesheet[row * 32: (row + 1) * 32, col * 32: (col + 1) * 32]
    mask = get_aspect_sprite_mask(aspect)
    sprite[~mask] = [102, 185, 226]
    return sprite


def get_aspect_sprite_mask(aspect: AspectType) -> np.ndarray:
    index = aspect_to_sprite_index[aspect]
    row = index // 16
    col = index % 16
    return spritesheet_alpha[row * 32: (row + 1) * 32, col * 32: (col + 1) * 32] > 100


aspect_to_sprite_index = {
    AER: 1,
    ALIENSIS: 2,
    AQUA: 3,
    ARBOR: 4,
    AURAM: 5,
    BESTIA: 6,
    COGNITIO: 7,
    CORPUS: 8,
    DESIDIA: 49,
    EXANIMIS: 9,
    FABRICO: 10,
    FAMES: 11,
    GELUM: 12,
    GULA: 50,
    HERBA: 13,
    HUMANUS: 14,
    IGNIS: 15,
    INFERNUS: 51,
    INSTRUMENTUM: 16,
    INVIDIA: 52,
    IRA: 53,
    ITER: 17,
    LIMUS: 18,
    LUCRUM: 19,
    LUX: 20,
    LUXURIA: 54,
    MACHINA: 21,
    MESSIS: 22,
    METALLUM: 23,
    METO: 24,
    MORTUUS: 25,
    MOTUS: 26,
    ORDO: 27,
    PANNUS: 28,
    PERDITIO: 29,
    PERFODIO: 30,
    PERMUTATIO: 31,
    POTENTIA: 32,
    PRAECANTATIO: 33,
    SANO: 34,
    SENSUS: 35,
    SPIRITUS: 36,
    SUPERBIA: 55,
    TELUM: 37,
    TEMPESTAS: 38,
    TEMPUS: 61,
    TENEBRAE: 39,
    TERMINUS: 73,
    TERRA: 40,
    TUTAMEN: 41,
    VACUOS: 42,
    VENEMUM: 43,
    VICTUS: 44,
    VINCULUM: 45,
    VITIUM: 46,
    VITREUS: 47,
    VOLATUS: 48,
}

