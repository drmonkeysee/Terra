"""Terra main application."""

import curses
import curses.panel
import enum
import logging

from terra.codepage import CP437


class KeyCode(enum.IntEnum):
    QUIT = ord('q')


def run() -> None:
    print('Starting Terra...')
    logging.basicConfig(filename='debug.log', filemode='w',
                        level=logging.DEBUG)
    curses.wrapper(_game_loop)
    print('Terra exited')


def _game_loop(stdscr):
    cppan = _codepage_box()
    inputpan = _input_box()
    while True:
        match stdscr.getch():
            case KeyCode.QUIT:
                break
            case c:
                inputpan.window().addch(c)
        curses.panel.update_panels()
        curses.doupdate()


def _codepage_box():
    dim = 16
    cpwin = curses.newwin(dim + 2, dim * 2 + 1, 5, 70)
    cppan = curses.panel.new_panel(cpwin)
    cpwin.box()
    for i, c in enumerate(CP437):
        y, x = divmod(i, dim)
        cpwin.addstr(y + 1, (x * 2) + 1, c)
    return cppan


def _input_box():
    inputwin = curses.newwin(25, 60, 3, 5)
    inputwin.box()
    inputpan = curses.panel.new_panel(inputwin)
    inputwin.addstr(1, 1, 'Hello from Terra!')
    inputwin.move(3, 1)
    return inputpan
