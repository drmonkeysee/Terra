"""Terra simulation models."""

import random


class Sim:
    """Primary simulation object."""

    def __init__(self) -> None:
        """Create new simulation."""
        self.create_map(0, 0)

    def create_map(self, height: int, width: int) -> None:
        """Generate a new world map.

        :param height: height of world map in cells
        :param width: width of world map in cells
        """
        self.world_map: SimpleMap = SimpleMap(height, width)


class SimpleMap:
    """A map composed of cells."""

    _CHAR_MAP: tuple[int, ...] = (0x20, 0x5, 0x6, 0x27, 0x2c, 0x3a, 0x3b)
    _WEIGHTS: tuple[int, ...] = tuple([100 - (5 * (len(_CHAR_MAP) - 1))]
                                      + ([5] * (len(_CHAR_MAP) - 1)))

    def __init__(self, height: int, width: int) -> None:
        """Generate a random map.

        :param height: height of world map in cells
        :param width: width of world map in cells
        """
        self.height = height
        self.width = width
        self.cells: tuple[int, ...] = self._buildcells()

    def _buildcells(self):
        return tuple(random.choices(self._CHAR_MAP, weights=self._WEIGHTS,
                                    k=self.height * self.width))
