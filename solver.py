from hexgrid import HexGrid, HexCoord
from aspects import *
from hexgrid.HexGrid import FREE, WALL


class ThaumSolver:
    grid: HexGrid

    def __init__(self, grid: HexGrid):
        self.grid = grid

    def solve(self) -> HexGrid:
        initial_points = []
        for coord, value in self.grid:
            if is_aspect(value):
                initial_points.append(coord)

        main_component = [initial_points.pop()]
        while initial_points:
            target = initial_points.pop()
            closest_point = min(main_component, key=lambda point: point.distance(target))
            self.fill_aspects_between_points(target, closest_point)

    def find_closest_aspect_hex(self, start: HexCoord) -> HexCoord:
        for radius in range(1, self.grid.radius * 2 + 1, 1):
            for hex_coord, hex_value in self.grid.iterate_radius(start, radius):
                if hex_value not in (FREE, WALL):
                    return hex_coord

    def find_aspects_between_points(self, p1: HexCoord, p2: HexCoord) -> tuple[list[HexCoord], list[AspectType]]:
        aspect1 = self.grid.get_data(p1)
        aspect2 = self.grid.get_data(p2)
        assert aspect1 not in [FREE, WALL]
        assert aspect2 not in [FREE, WALL]

        coords_path = self.grid.get_shortest_path(p1, p2)
        aspect_path = aspect_utils.find_shortest_path(aspect1, aspect2)

        if len(coords_path) < len(aspect_path):
            coords_path = self.grid.get_path(p1, p2, len(aspect_path))
        else:
            aspect_path = aspect_utils.find_path(aspect1, aspect2, len(coords_path))

        return coords_path, aspect_path

    def fill_aspects_between_points(self, p1: HexCoord, p2: HexCoord):
        coords, aspects = self.find_aspects_between_points(p1, p2)
        for coord, aspect in zip(coords, aspects):
            self.grid.set_data(coord, aspect)

    def print_grid(self):
        for coord, value in self.grid:
            if is_aspect(value):
                self.grid.set_data(coord, to_string(value)[:3])
        print(self.grid)


def is_aspect(value: int) -> bool:
    return value not in [FREE, WALL]
