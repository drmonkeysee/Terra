"""Curses UI layer, including main game/event loop."""

from __future__ import annotations

import curses
import curses.panel
import enum
import typing

from terra.codepage import CP437
if typing.TYPE_CHECKING:
    from terra.sim import Sim


def start(sim: Sim) -> None:
    """Start the main game loop.

    :param sim: simulation object
    """
    curses.wrapper(_main_loop, sim)


class _KeyCode(enum.IntEnum):
    GEN_MAP = ord('m')
    QUIT = ord('q')
    TOGGLE_CODEPAGE = ord('c')


def _main_loop(stdscr, sim):
    cppan = _codepage_panel()
    cppan.hide()
    mappan = _map_panel(stdscr)
    _new_map(mappan.window(), sim)
    echopan = _echo_panel()
    while True:
        match stdscr.getch():
            case _KeyCode.GEN_MAP:
                _new_map(mappan.window(), sim)
            case _KeyCode.QUIT:
                break
            case _KeyCode.TOGGLE_CODEPAGE:
                if cppan.hidden():
                    cppan.show()
                else:
                    cppan.hide()
            case c:
                echopan.window().addch(c)
        curses.panel.update_panels()
        curses.doupdate()


def _codepage_panel():
    dim = 16
    win = curses.newwin(dim + 2, dim * 2 + 1, 5, 70)
    panel = curses.panel.new_panel(win)
    win.box()
    for i, c in enumerate(CP437):
        y, x = divmod(i, dim)
        win.addstr(y + 1, (x * 2) + 1, c)
    return panel


def _map_panel(stdscr):
    w, h = 102, 32
    screenh, screenw = stdscr.getmaxyx()
    win = curses.newwin(h, w, (screenh - h) // 2, (screenw - w) // 2)
    panel = curses.panel.new_panel(win)
    win.box()
    return panel


def _new_map(map_win, sim):
    h, w = (c - 2 for c in map_win.getmaxyx())
    sim.create_map(h, w)
    for i, c in enumerate(sim.world_map.cells):
        y, x = divmod(i, w)
        map_win.addstr(y + 1, x + 1, CP437[c])


def _echo_panel():
    win = curses.newwin(10, 20, 3, 5)
    panel = curses.panel.new_panel(win)
    win.box()
    win.addstr(1, 1, 'Hello from Terra!')
    win.move(3, 1)
    return panel
