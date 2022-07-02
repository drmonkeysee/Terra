"""Terra main application."""

import curses
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
    stdscr.addstr(3, 5, 'Hello from Terra!')
    cpwin = _draw_codepage()
    stdscr.move(4, 5)
    while True:
        match stdscr.getch():
            case KeyCode.QUIT:
                break
            case c:
                stdscr.addch(c)
        cpwin.noutrefresh()


def _draw_codepage():
    cpwin = curses.newwin(18, 18, 5, 20)
    cpwin.box()
    cpwin.move(0, 0)
    for i, c in enumerate(CP437):
        if i % 16 == 0:
            cursor = cpwin.getyx()
            logging.debug('iter %d: pos %s', i, cursor)
            cpwin.move(cursor[0] + 1, 1)
        cpwin.addstr(c)
    return cpwin
