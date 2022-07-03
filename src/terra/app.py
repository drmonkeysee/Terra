"""Terra main application."""

import curses
import curses.panel
import enum
import logging
import random

from terra.codepage import CP437


class KeyCode(enum.IntEnum):
    GEN_MAP = ord('m')
    QUIT = ord('q')
    TOGGLE_CODEPAGE = ord('c')


class SimpleMap:
    CHAR_MAP: tuple[int, ...] = (0x20, 0x5, 0x6, 0x27, 0x2c, 0x3a, 0x3b)
    WEIGHTS: tuple[int, ...] = (70, 5, 5, 5, 5, 5, 5)

    def __init__(self, height: int, width: int) -> None:
        self.height = height
        self.width = width
        self.cells: list[int] = self._buildcells()

    def _buildcells(self):
        return random.choices(self.CHAR_MAP, weights=self.WEIGHTS,
                              k=self.height * self.width)


def run() -> None:
    print('Starting Terra...')
    logging.basicConfig(filename='debug.log', filemode='w',
                        level=logging.DEBUG)
    random.seed(0)
    curses.wrapper(_game_loop)
    print('Terra exited')


def _game_loop(stdscr):
    cppan = _codepage_panel()
    cppan.hide()
    mappan = _map_panel(stdscr)
    _new_map(mappan.window())
    echopan = _echo_panel()
    while True:
        match stdscr.getch():
            case KeyCode.GEN_MAP:
                _new_map(mappan.window())
            case KeyCode.QUIT:
                break
            case KeyCode.TOGGLE_CODEPAGE:
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


def _new_map(map_win):
    h, w = (c - 2 for c in map_win.getmaxyx())
    worldmap = SimpleMap(h, w)
    logging.debug('map cells %s', worldmap.cells)
    for i, c in enumerate(worldmap.cells):
        y, x = divmod(i, w)
        map_win.addstr(y + 1, x + 1, CP437[c])


def _echo_panel():
    win = curses.newwin(10, 20, 3, 5)
    panel = curses.panel.new_panel(win)
    win.box()
    win.addstr(1, 1, 'Hello from Terra!')
    win.move(3, 1)
    return panel
