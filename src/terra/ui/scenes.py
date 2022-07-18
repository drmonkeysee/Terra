"""Game Scenes."""

from __future__ import annotations

import enum
import typing

from terra.sim import Simulation
from terra.ui.views import CodePageView, FrameMetricsView, MapView

if typing.TYPE_CHECKING:
    import curses
    from terra.ui.clock import FrameData


class WorldScene:
    """Primary scene for Terra.

    Displays and mediates the primary simulation.
    """

    def __init__(self, stdscr: curses.window) -> None:
        """Initialize a world scene.

        Args:
            stdscr: The main curses window.
        """
        self.stdscr = stdscr
        self._sim = Simulation()
        self._layout_views()

    def handle_input(self) -> bool:
        """Process user input.

        Returns:
            Whether the main loop should continue or not.
        """
        match self.stdscr.getch():
            case _KeyCode.GEN_MAP:
                self._new_map()
            case _KeyCode.QUIT:
                return False
            case _KeyCode.TOGGLE_CODEPAGE:
                self._codepage_view.toggle_visibility()
        return True

    def update(self, frame: FrameData) -> None:
        """Update the scene for the given frame.

        Args:
            frame: The current frame data.
        """
        self._sim.update(frame.delta_ms)
        self._redraw(frame)

    def _layout_views(self):
        # NOTE: measure left-pane from codepage view dimensions but place
        # codepage below frame metrics once both windows' dimensions are known.
        self._codepage_view = CodePageView(0, 0)
        left_pane_w = self._codepage_view.frame.getmaxyx()[1]
        self._metrics_view = FrameMetricsView(left_pane_w, 0, 0)
        self._codepage_view.frame.mvwin(self._metrics_view.frame.getmaxyx()[0],
                                        0)
        screen_h, screen_w = self.stdscr.getmaxyx()
        self._map_view = MapView(screen_h, screen_w - left_pane_w, 0,
                                 left_pane_w)
        self._new_map()

    def _redraw(self, frame):
        self._metrics_view.redraw(frame)
        self._map_view.redraw(self._sim.visible_map)

    def _new_map(self):
        self._sim.create_map(*self._map_view.content.getmaxyx())


class _KeyCode(enum.IntEnum):
    GEN_MAP = ord('m')
    QUIT = ord('q')
    TOGGLE_CODEPAGE = ord('c')
