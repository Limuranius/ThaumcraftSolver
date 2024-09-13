# Flat top orientation (double-height)
# odd-q


def doubleheight_to_axial(col, row):
    q = col
    r = (row - col) / 2
    return q, r


def axial_to_doubleheight(q, r):
    col = q
    row = 2 * r + q
    return col, row


def cube_to_axial(q, r, s):
    return q, r


def axial_to_cube(q, r):
    s = -q - r
    return q, r, s


class HexCoord:
    __axial: tuple[int, int]  # q, r

    @property
    def axial(self) -> tuple[int, int]:
        # q, r
        return self.__axial

    @property
    def doubled(self) -> tuple[int, int]:
        # col, row
        return axial_to_doubleheight(*self.__axial)

    @property
    def cube(self) -> tuple[int, int, int]:
        # q, r, s
        return axial_to_cube(*self.__axial)

    @classmethod
    def from_doubled(cls, col: int, row: int):
        coords = HexCoord()
        coords.__axial = doubleheight_to_axial(col, row)
        return coords

    @classmethod
    def from_axial(cls, q: int, r: int):
        coords = HexCoord()
        coords.__axial = (q, r)
        return coords

    def __repr__(self):
        # return "Doubled: " + str(self.doubled)
        return str(self.axial)

    def __eq__(self, other):
        return self.axial == other.axial

    def __add__(self, other):
        return HexCoord.from_axial(
            self.axial[0] + other.axial[0],
            self.axial[1] + other.axial[1],
        )

    def __sub__(self, other):
        return HexCoord.from_axial(
            self.axial[0] - other.axial[0],
            self.axial[1] - other.axial[1],
        )

    def neighbor(self, direction_index):
        return self + NEIGHBOR_DIRECTIONS[direction_index]

    def scale(self, factor: int):
        q, r = self.__axial
        return HexCoord.from_axial(q * factor, r * factor)

    def distance_from_center(self):
        q, r = self.axial
        return (abs(q) + abs(q + r) + abs(r)) // 2

    def distance(self, other):
        vec = self - other
        q, r = vec.axial
        return (abs(q) + abs(q + r) + abs(r)) // 2


NEIGHBOR_DIRECTIONS = [
    HexCoord.from_axial(+1, 0),
    HexCoord.from_axial(+1, -1),
    HexCoord.from_axial(0, -1),
    HexCoord.from_axial(-1, 0),
    HexCoord.from_axial(-1, +1),
    HexCoord.from_axial(0, +1),
]
