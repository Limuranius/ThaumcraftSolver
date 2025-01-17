from collections import defaultdict

from custom_types import PathNotFoundException
from .HexCoord import HexCoord, NEIGHBOR_DIRECTIONS

FREE = -1
WALL = -2


# https://www.redblobgames.com/grids/hexagons/
class HexGrid:
    radius: int
    data: list[list[...]]  # Axial coordinates (q, r)

    def __init__(self, radius: int):
        self.radius = radius
        self.data = [[FREE for _ in range(radius * 2 + 1)] for __ in range(radius * 2 + 1)]

    def __str__(self):
        R = self.radius
        output = [[" " for _ in range(R * 2 + 1)] for __ in range(R * 4 + 1)]
        for cell_coord, cell_data in self:
            col, row = cell_coord.doubled
            output[row + R * 2][col + R] = str(cell_data)
        s = ""
        for row in output:
            s += "   ".join(row) + "\n"
        return s

    def __iter__(self) -> tuple[HexCoord, ...]:
        N = self.radius
        for q in range(-N, N + 1, 1):
            for r in range(max(-N, -q - N), min(N, -q + N) + 1, 1):
                cell_coord = HexCoord.from_axial(q, r)
                cell_data = self.get_data(cell_coord)
                yield cell_coord, cell_data

    def iterate_radius(self, center: HexCoord, radius: int) -> tuple[HexCoord, ...]:
        ring_hex = center + NEIGHBOR_DIRECTIONS[4].scale(radius)
        for direction_index in range(6):
            for _ in range(radius):
                in_bounds = ring_hex.distance_from_center() <= self.radius
                if in_bounds:
                    yield ring_hex, self.get_data(ring_hex)
                ring_hex = ring_hex.neighbor(direction_index)

    def set_data(self, coord: HexCoord, value):
        q, r = coord.axial
        self.data[q][r] = value

    def get_data(self, coord: HexCoord):
        q, r = coord.axial
        return self.data[q][r]

    def get_shortest_path(self, start: HexCoord, end: HexCoord) -> list[HexCoord]:
        paths_queue = [[start]]
        visited = defaultdict(bool)
        while paths_queue:
            path = paths_queue.pop(0)
            path_last_coord = path[-1]
            if path_last_coord == end:
                return path
            else:
                for direction_index in range(6):
                    new_coord = path_last_coord.neighbor(direction_index)
                    in_bounds = new_coord.distance_from_center() <= self.radius
                    is_end = new_coord == end
                    is_free = self.get_data(new_coord) == FREE
                    if in_bounds and (is_free or is_end) and not visited[new_coord.axial]:
                        visited[new_coord.axial] = True
                        new_path = list(path) + [new_coord]
                        paths_queue.append(new_path)
        raise PathNotFoundException(f"Path not found: {start=} {end=}")

    def get_path(self, start: HexCoord, end: HexCoord, length: int) -> list[HexCoord]:
        answer = [None] * length
        visited = defaultdict(bool)

        def dfs(coord: HexCoord, curr_len: int) -> bool:
            answer[curr_len - 1] = coord
            if curr_len == length:
                if coord == end:
                    return True
                else:
                    return False
            visited[coord.axial] = True
            for direction_index in range(6):
                new_coord = coord.neighbor(direction_index)
                in_bounds = new_coord.distance_from_center() <= self.radius
                is_end = new_coord == end
                is_free = self.get_data(new_coord) == FREE
                if in_bounds and (is_free or is_end) and not visited[new_coord.axial]:
                    found_answer = dfs(new_coord, curr_len + 1)
                    if found_answer:
                        return True
            visited[coord.axial] = False
            return False

        found_path = dfs(start, 1)
        if found_path:
            return answer
        else:
            raise PathNotFoundException(f"Path not found: {start=} {end=} {length=}")
