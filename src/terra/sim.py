import random


class Sim:
    def __init__(self) -> None:
        self.create_map(0, 0)

    def create_map(self, height: int, width: int) -> None:
        self.world_map: SimpleMap = SimpleMap(height, width)


class SimpleMap:
    CHAR_MAP: tuple[int, ...] = (0x20, 0x5, 0x6, 0x27, 0x2c, 0x3a, 0x3b)
    WEIGHTS: tuple[int, ...] = tuple([100 - (5 * (len(CHAR_MAP) - 1))]
                                     + ([5] * (len(CHAR_MAP) - 1)))

    def __init__(self, height: int, width: int) -> None:
        self.height = height
        self.width = width
        self.cells: tuple[int, ...] = self._buildcells()

    def _buildcells(self):
        return tuple(random.choices(self.CHAR_MAP, weights=self.WEIGHTS,
                                    k=self.height * self.width))
