"""Terra UI layer, including the main game loop."""

from __future__ import annotations

import curses
import curses.panel
import enum
import typing

from terra.ui.clock import FrameClock
from terra.ui.views import (
    CodePageView, FrameMetricsView, MapView, center_in_win
)

if typing.TYPE_CHECKING:
    from terra.sim import Simulation


def start(sim: Simulation) -> None:
    """Start the main game loop."""
    curses.wrapper(_main_loop, sim)


class _KeyCode(enum.IntEnum):
    GEN_MAP = ord('m')
    QUIT = ord('q')
    TOGGLE_CODEPAGE = ord('c')


def _main_loop(stdscr, sim):
    stdscr.nodelay(True)
    curses.curs_set(0)
    frame_clock = FrameClock()
    running = True

    scene = _Scene(stdscr, sim)
    while running:
        with frame_clock as next_frame:
            running = scene.handle_input()
            if running:
                scene.update(next_frame)
                _refresh_ui()


def _refresh_ui():
    curses.panel.update_panels()
    curses.doupdate()


class _Scene:
    def __init__(self, stdscr, sim):
        self.stdscr = stdscr
        self.sim = sim
        self._layout_views()

    def handle_input(self):
        match self.stdscr.getch():
            case _KeyCode.GEN_MAP:
                self._new_map()
            case _KeyCode.QUIT:
                return False
            case _KeyCode.TOGGLE_CODEPAGE:
                self._codepage_view.toggle_visibility()
        return True

    def update(self, frame):
        self.sim.update(frame.delta_ms)
        self._redraw(frame)

    def _layout_views(self):
        self._codepage_view = CodePageView(5, 70)
        self._codepage_view.toggle_visibility()
        self._map_view = MapView(*center_in_win(self.stdscr, 32, 102))
        self._metrics_view = FrameMetricsView(15, 5)
        self._new_map()

    def _redraw(self, frame):
        self._metrics_view.redraw(frame)

    def _new_map(self):
        self.sim.create_map(*self._map_view.content.getmaxyx())
        self._map_view.draw_map(self.sim.world_map)
