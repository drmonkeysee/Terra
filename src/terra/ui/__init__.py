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

    codepage_view = CodePageView(5, 70)
    codepage_view.toggle_visibility()
    map_view = MapView(*center_in_win(stdscr, 32, 102))
    _new_map(map_view, sim)
    metrics_view = FrameMetricsView(15, 5)

    frame_clock = FrameClock()
    running = True
    while running:
        with frame_clock as next_frame:
            running = _process_input(stdscr, codepage_view, map_view, sim)
            if running:
                sim.update(next_frame.delta_ms)
                _redraw(metrics_view, next_frame, sim)


def _process_input(stdscr, codepage_view, map_view, sim):
    match stdscr.getch():
        case _KeyCode.GEN_MAP:
            _new_map(map_view, sim)
        case _KeyCode.QUIT:
            return False
        case _KeyCode.TOGGLE_CODEPAGE:
            codepage_view.toggle_visibility()
    return True


def _redraw(metrics_view, frame, sim):
    metrics_view.draw(frame, sim)
    curses.panel.update_panels()
    curses.doupdate()


def _new_map(map_view, sim):
    sim.create_map(*map_view.content.getmaxyx())
    map_view.draw_map(sim.world_map)
