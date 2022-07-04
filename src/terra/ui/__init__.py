"""Curses UI layer, including main game/event loop."""

from __future__ import annotations

import curses
import curses.panel
import enum
import typing

from terra.codepage import CP437
if typing.TYPE_CHECKING:
    from terra.sim import Simulation
from terra.ui.views import CodePageView, EchoInputView


def start(sim: Simulation) -> None:
    """Start the main game loop.

    :param sim: simulation object
    """
    curses.wrapper(_main_loop, sim)


class _KeyCode(enum.IntEnum):
    GEN_MAP = ord('m')
    QUIT = ord('q')
    TOGGLE_CODEPAGE = ord('c')
    TOGGLE_ECHO = ord('o')


def _main_loop(stdscr, sim):
    cpview = CodePageView(5, 70)
    cpview.toggle_visibility()
    mapview = _map_view(stdscr)
    _new_map(mapview.window(), sim)
    echoview = EchoInputView(10, 20, 3, 5)
    while True:
        match stdscr.getch():
            case _KeyCode.GEN_MAP:
                _new_map(mapview.window(), sim)
            case _KeyCode.QUIT:
                break
            case _KeyCode.TOGGLE_CODEPAGE:
                cpview.toggle_visibility()
            case _KeyCode.TOGGLE_ECHO:
                echoview.toggle_visibility()
            case c:
                echoview.echoch(c)
        curses.panel.update_panels()
        curses.doupdate()


def _map_view(stdscr):
    w, h = 102, 32
    screenh, screenw = stdscr.getmaxyx()
    return _create_view(h, w, (screenh - h) // 2, (screenw - w) // 2,
                        title='Terra')


def _new_map(map_win, sim):
    h, w = (c - 2 for c in map_win.getmaxyx())
    sim.create_map(h, w)
    for i, c in enumerate(sim.world_map.cells):
        y, x = divmod(i, w)
        map_win.addstr(y + 1, x + 1, CP437[c])


def _create_view(h, w, y, x, /, *, title=None):
    win = curses.newwin(h, w, y, x)
    pan = curses.panel.new_panel(win)
    win.box()
    if title:
        padding = 2
        if len(title) > w - (padding * 2):
            title = f'{title[:-2]}…'
        win.addstr(0, padding, title)
    return pan
