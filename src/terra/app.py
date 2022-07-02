"""Terra main application."""

import curses
import enum


class KeyCode(enum.IntEnum):
    QUIT = ord('q')


def run() -> None:
    print('Starting Terra...')
    curses.wrapper(_game_loop)
    print('Terra exited')


def _game_loop(stdscr):
    stdscr.addstr(3, 5, 'Hello from Terra!')
    stdscr.move(4, 5)
    while True:
        match stdscr.getch():
            case KeyCode.QUIT:
                break
            case c:
                stdscr.addch(c)
