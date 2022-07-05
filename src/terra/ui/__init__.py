"""Curses UI layer, including main game/event loop."""

from __future__ import annotations

import curses
import curses.panel
import enum
import typing

if typing.TYPE_CHECKING:
    from terra.sim import Simulation
from terra.ui.views import (
    CodePageView, EchoInputView, FrameMetricsView, MapView, center_in_win
)


def start(sim: Simulation) -> None:
    """Start the main game loop."""
    curses.wrapper(_main_loop, sim)


class _KeyCode(enum.IntEnum):
    GEN_MAP = ord('m')
    QUIT = ord('q')
    TOGGLE_CODEPAGE = ord('c')
    TOGGLE_ECHO = ord('o')


def _main_loop(stdscr, sim):
    codepage_view = CodePageView(5, 70)
    codepage_view.toggle_visibility()
    map_view = MapView(*center_in_win(stdscr, 32, 102))
    _new_map(map_view, sim)
    echo_view = EchoInputView(10, 20, 3, 5)
    metrics_view = FrameMetricsView(15, 5)
    while _process_input(stdscr, codepage_view, map_view, echo_view, sim):
        _update(sim)
        _redraw(metrics_view, sim)


def _process_input(stdscr, codepage_view, map_view, echo_view, sim):
    match stdscr.getch():
        case _KeyCode.GEN_MAP:
            _new_map(map_view, sim)
        case _KeyCode.QUIT:
            return False
        case _KeyCode.TOGGLE_CODEPAGE:
            codepage_view.toggle_visibility()
        case _KeyCode.TOGGLE_ECHO:
            echo_view.toggle_visibility()
        case c:
            echo_view.echoch(c)
    return True


def _update(sim):
    sim.update()


def _redraw(metrics_view, sim):
    metrics_view.draw(sim)
    curses.panel.update_panels()
    curses.doupdate()


def _new_map(map_view, sim):
    sim.create_map(*map_view.content.getmaxyx())
    map_view.draw_map(sim.world_map)
