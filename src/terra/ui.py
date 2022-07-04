"""Curses UI layer, including main game/event loop."""

from __future__ import annotations

import curses
import curses.panel
import enum
import typing

from terra.codepage import CP437
if typing.TYPE_CHECKING:
    from terra.sim import Simulation


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
    cpview = _codepage_view()
    cpview.hide()
    mapview = _map_view(stdscr)
    _new_map(mapview.window(), sim)
    echoview, echocontent = _echo_view()
    while True:
        match stdscr.getch():
            case _KeyCode.GEN_MAP:
                _new_map(mapview.window(), sim)
            case _KeyCode.QUIT:
                break
            case _KeyCode.TOGGLE_CODEPAGE:
                if cpview.hidden():
                    cpview.show()
                else:
                    cpview.hide()
            case _KeyCode.TOGGLE_ECHO:
                if echoview.hidden():
                    echoview.show()
                    echocontent.show()
                else:
                    echocontent.hide()
                    echoview.hide()
            case c:
                echocontent.window().addch(c)
        curses.panel.update_panels()
        curses.doupdate()


def _codepage_view():
    dim = 16
    height = dim + 4
    width = (dim * 2) + 3
    view = _create_view(height, width, 5, 70, title='Code Page 437')
    view.window().addstr(1, 1, '\\')
    view.window().hline(2, 1, 0, width - 2)
    view.window().vline(1, 2, 0, height - 2)
    view.window().addch(2, 0, curses.ACS_LTEE)
    view.window().addch(2, 2, curses.ACS_PLUS)
    view.window().addch(2, width - 1, curses.ACS_RTEE)
    view.window().addch(height - 1, 2, curses.ACS_BTEE)
    grid_pad = 3
    for i in range(dim):
        view.window().addstr(1, (i * 2) + grid_pad, f'{i:X}')
    for i, c in enumerate(CP437):
        y, x = divmod(i, dim)
        view.window().addstr(y + grid_pad, 1, f'{y:X}')
        view.window().addstr(y + grid_pad, (x * 2) + grid_pad, c)
    return view


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


def _echo_view():
    view = _create_view(10, 20, 3, 5)
    contentwin = view.window().derwin(8, 18, 1, 1)
    contentwin.addstr(0, 0, 'Hello from Terra!')
    contentwin.move(2, 0)
    return view, curses.panel.new_panel(contentwin)


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
