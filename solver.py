from collections import defaultdict

from aspects import *
from custom_types import AspectType, PathNotFoundException
from hexgrid import HexGrid, HexCoord
from hexgrid.HexGrid import FREE, WALL


class ThaumSolver:
    grid: HexGrid

    def __init__(self, grid: HexGrid):
        self.grid = grid

    def solve(self) -> None:
        initial_points = self.find_aspects_coords()
        main_component = [initial_points.pop()]
        while initial_points:
            self.print_grid()
            target = initial_points.pop()

            sorted_by_distance = self.sort_points_by_distance(target, main_component)

            path_found = False
            while sorted_by_distance and not path_found:
                component_point = sorted_by_distance.pop(0)
                try:
                    coords, aspects = self.find_aspects_between_points(target, component_point)
                    main_component += coords
                    self.fill_aspects_between_points(target, component_point)
                    path_found = True
                except PathNotFoundException:
                    print("Path not found, trying another point")
            if not path_found:
                raise PathNotFoundException("Solution not found :(")

    def find_closest_component_point(self, start: HexCoord, component: list[HexCoord]) -> HexCoord:
        visited = defaultdict(bool)
        q = [start]
        while q:
            coord = q.pop(0)
            if coord in component:
                return coord
            else:
                for direction_index in range(6):
                    new_coord = coord.neighbor(direction_index)
                    in_bounds = new_coord.distance_from_center() <= self.grid.radius
                    is_component = new_coord in component
                    is_free = self.grid.get_data(new_coord) == FREE
                    if in_bounds and (is_free or is_component) and not visited[new_coord.axial]:
                        visited[new_coord.axial] = True
                        q.append(new_coord)
        raise Exception("find_closest_component_point did not find path")

    def sort_points_by_distance(self, start: HexCoord, points: list[HexCoord]) -> list[HexCoord]:
        # Runs BFS starting from 'start' to 'points' and sorts
        # in ascending order based on BFS results
        visited = defaultdict(bool)
        q = [start]
        sorted_points = []
        while q:
            coord = q.pop(0)
            if coord in points:
                sorted_points.append(coord)
            else:
                for direction_index in range(6):
                    new_coord = coord.neighbor(direction_index)
                    in_bounds = new_coord.distance_from_center() <= self.grid.radius
                    in_points = new_coord in points
                    is_free = self.grid.get_data(new_coord) == FREE
                    if in_bounds and (is_free or in_points) and not visited[new_coord.axial]:
                        visited[new_coord.axial] = True
                        q.append(new_coord)
        return sorted_points

    def find_aspects_coords(self) -> list[HexCoord]:
        coords = []
        for coord, value in self.grid:
            if is_aspect(value):
                coords.append(coord)
        return coords

    def find_closest_aspect_hex(self, start: HexCoord) -> HexCoord:
        for radius in range(1, self.grid.radius * 2 + 1, 1):
            for hex_coord, hex_value in self.grid.iterate_radius(start, radius):
                if hex_value not in (FREE, WALL):
                    return hex_coord

    def find_aspects_between_points(self, p1: HexCoord, p2: HexCoord) -> tuple[list[HexCoord], list[AspectType]]:
        aspect1 = self.grid.get_data(p1)
        aspect2 = self.grid.get_data(p2)
        assert is_aspect(aspect1)
        assert is_aspect(aspect2)

        coords_path = self.grid.get_shortest_path(p1, p2)
        path_len = len(coords_path)

        while True:
            try:
                aspect_path = aspect_utils.find_path(aspect1, aspect2, path_len)
                return coords_path, aspect_path
            except PathNotFoundException:
                path_len += 1
                coords_path = self.grid.get_path(p1, p2, path_len)

    def fill_aspects_between_points(self, p1: HexCoord, p2: HexCoord):
        coords, aspects = self.find_aspects_between_points(p1, p2)
        for coord, aspect in zip(coords, aspects):
            self.grid.set_data(coord, aspect)

    def print_grid(self):
        pretty_grid = HexGrid(self.grid.radius)
        for coord, value in self.grid:
            if is_aspect(value):
                pretty_grid.set_data(coord, to_string(value)[:3])
            else:
                pretty_grid.set_data(coord, value)
        print(pretty_grid)


def is_aspect(value: int) -> bool:
    return value not in [FREE, WALL]
