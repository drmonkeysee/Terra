"""Terra simulation models."""

import enum
import random


class Simulation:
    """Primary simulation object."""

    def __init__(self) -> None:
        """Initialize a new simulation.

        Attributes:
            world_map: the current map of the world.
        """
        self._entities = []

    @property
    def visible_map(self) -> list[int]:
        tiles = self.world_map.cells.copy()
        for entity in self._entities:
            tiles[entity.x + (entity.y * self.width)] = entity.render_id
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
        self._entities.append(_Wanderer(random.randrange(height),
                                        random.randrange(width)))
        self._entities.append(_Zipper(random.randrange(height),
                                      random.randrange(width)))
        self._entities.append(_Bouncer(random.randrange(height),
                                       random.randrange(width)))

    def update(self, elapsed: float) -> None:
        """Run the simulation for a given time-slice.

        Args:
            elapsed: time since last update in fractional milliseconds.
        """
        for entity in self._entities:
            entity.update(elapsed, self.height, self.width)


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


class _Direction(enum.Enum):
    RIGHT = enum.auto()
    UP = enum.auto()
    LEFT = enum.auto()
    DOWN = enum.auto()

    def reverse(self):
        match self:
            case _Direction.RIGHT:
                return _Direction.LEFT
            case _Direction.UP:
                return _Direction.DOWN
            case _Direction.LEFT:
                return _Direction.RIGHT
            case _Direction.DOWN:
                return _Direction.UP


# TODO: these are all way too coupled to everything else
class _Wanderer:
    _VELOCITY = 200

    def __init__(self, y, x):
        self.y = y
        self.x = x
        self._energy = 0.0
        self.render_id = 0x40

    def update(self, elapsed, screenh, screenw):
        self._energy += elapsed
        if self._energy > self._VELOCITY:
            y, x = self._move()
            if 0 <= y < screenh and 0 <= x < screenw:
                self.y, self.x = y, x
            self._energy = 0.0

    def _move(self):
        match random.choice(tuple(_Direction)):
            case _Direction.RIGHT:
                return self.y, self.x + 1
            case _Direction.UP:
                return self.y - 1, self.x
            case _Direction.LEFT:
                return self.y, self.x - 1
            case _Direction.DOWN:
                return self.y + 1, self.x


class _Zipper:
    _VELOCITY = 50
    _SHIFT = 1000

    def __init__(self, y, x):
        self.y = y
        self.x = x
        self._attention = self._energy = 0.0
        self._direction = _Direction.RIGHT

    @property
    def render_id(self):
        return (0x1a, 0x18, 0x1b, 0x19)[self._direction.value - 1]

    def update(self, elapsed, screenh, screenw):
        self._energy += elapsed
        self._attention += elapsed
        if self._energy > self._VELOCITY:
            self._energy = 0.0
            y, x = self._move()
            if 0 <= y < screenh and 0 <= x < screenw:
                self.y, self.x = y, x
            else:
                self._direction = self._direction.reverse()
        if self._attention > self._SHIFT:
            self._attention = 0.0
            self._direction = random.choice(tuple(_Direction))

    def _move(self):
        match self._direction:
            case _Direction.RIGHT:
                return self.y, self.x + 1
            case _Direction.UP:
                return self.y - 1, self.x
            case _Direction.LEFT:
                return self.y, self.x - 1
            case _Direction.DOWN:
                return self.y + 1, self.x


class _Bouncer:
    _VELOCITY = 100

    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.render_id = 0xe8
        self._energy = 0.0
        self._directions = [_Direction.UP, _Direction.RIGHT]
        self._active_direction = 0

    def update(self, elapsed, screenh, screenw):
        self._energy += elapsed
        if self._energy > self._VELOCITY:
            y, x = self._move()
            if y < 0 or y >= screenh:
                self._directions[0] = self._directions[0].reverse()
            elif x < 0 or x >= screenw:
                self._directions[1] = self._directions[1].reverse()
            else:
                self.y, self.x = y, x
                self._active_direction = (self._active_direction + 1) % 2
            self._energy = 0.0

    def _move(self):
        match self._directions[self._active_direction]:
            case _Direction.RIGHT:
                return self.y, self.x + 1
            case _Direction.UP:
                return self.y - 1, self.x
            case _Direction.LEFT:
                return self.y, self.x - 1
            case _Direction.DOWN:
                return self.y + 1, self.x
