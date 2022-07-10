"""Terra simulation models."""

import random


class Simulation:
    """Primary simulation object."""

    def __init__(self) -> None:
        """Initialize a new simulation."""
        self.create_map(0, 0)
        self.sim_value: int = 0

    def create_map(self, height: int, width: int) -> None:
        """Generate a new world map.

        Args:
            height: height of world map in cells.
            width: width of world map in cells.

        Attributes:
            world_map: the current map of the world.
        """
        self.world_map: SimpleMap = SimpleMap(height * width)

    def update(self, elapsed: float) -> None:
        """Run the simulation for a given time-slice.

        Args:
            elapsed: time since last update in fractional milliseconds.
        """
        self.sim_value += 1


class SimpleMap:
    """A map composed of cells.

    Cells are indexes into a code page, which resolves to a specific glyph.
    """

    _CHAR_MAP: tuple[int, ...] = (0x20, 0x5, 0x6, 0x27, 0x2c, 0x3a, 0x3b)
    _WEIGHTS: tuple[int, ...] = tuple([100 - (5 * (len(_CHAR_MAP) - 1))]
                                      + ([5] * (len(_CHAR_MAP) - 1)))

    def __init__(self, size: int) -> None:
        """Generate a random map.

        Args:
            size: size of world map in cells.

        Attributes:
            size: size of world map in cells.
            cells: the cells making up the map.
        """
        self.size = size
        self.cells: tuple[int, ...] = self._buildcells()

    def _buildcells(self):
        cells = random.choices(self._CHAR_MAP, weights=self._WEIGHTS,
                               k=self.size)
        if cells:
            cells[0] = 0x41     # 'A'
            cells[-1] = 0x5a    # 'Z'
        return tuple(cells)
