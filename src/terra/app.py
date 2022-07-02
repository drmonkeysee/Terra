"""Terra main application."""

import curses
import enum


class InputCode(enum.IntEnum):
    QUIT = ord('q')


def run() -> None:
    print('Starting Terra...')
    curses.wrapper(_game_loop)
    print('Terra exited')


def _game_loop(stdscr):
    stdscr.addstr(3, 5, 'Hello from Terra!')
    stdscr.move(4, 5)
    running = True
    while running:
        match stdscr.getch():
            case InputCode.QUIT:
                running = False
            case c:
                stdscr.addch(c)
