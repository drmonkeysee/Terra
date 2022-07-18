"""Terra simulation models."""

import random


class Simulation:
    """Primary simulation object."""

    def __init__(self) -> None:
        """Initialize a new simulation.

        Attributes:
            world_map: the current map of the world.
        """
        self.create_map(0, 0)
        self._wanderer = Wanderer(0, 0)

    @property
    def visible_map(self) -> list[int]:
        tiles = self.world_map.cells.copy()
        tiles[self._wanderer.x
              + (self._wanderer.y * self.width)] = self._wanderer.render_id
        return tiles

    def create_map(self, height: int, width: int) -> None:
        """Generate a new world map.

        Args:
            height: height of world map in cells.
            width: width of world map in cells.
        """
        self.world_map: SimpleMap = SimpleMap(height * width)
        self.height = height
        self.width = width

    def update(self, elapsed: float) -> None:
        """Run the simulation for a given time-slice.

        Args:
            elapsed: time since last update in fractional milliseconds.
        """
        self._wanderer.update(elapsed, self.height, self.width)


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
        self.cells: list[int] = self._buildcells()

    def _buildcells(self):
        return random.choices(self._CHAR_MAP, weights=self._WEIGHTS,
                              k=self.size)


class Wanderer:
    # TODO: this is way too coupled to everything else
    _THRESHOLD = 100

    def __init__(self, y, x):
        self.y = y
        self.x = x
        self._energy = 0.0
        self.render_id = 0x40

    def update(self, elapsed, screenh, screenw):
        self._energy += elapsed
        if self._energy > self._THRESHOLD:
            y, x = self._move()
            if 0 <= y < screenh and 0 <= x < screenw:
                self.y, self.x = y, x
            self._energy = 0.0

    def _move(self):
        match random.randint(1, 4):
            case 1:
                return self.y, self.x + 1
            case 2:
                return self.y - 1, self.x
            case 3:
                return self.y, self.x - 1
            case 4:
                return self.y + 1, self.x
