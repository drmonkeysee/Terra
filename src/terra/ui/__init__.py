"""Terra UI layer, including the main game loop."""

import curses
import curses.panel

from terra.ui.clock import FrameClock
from terra.ui.scenes import WorldScene


def start() -> None:
    """Start the main game loop."""
    curses.wrapper(_main_loop)


def _main_loop(stdscr):
    stdscr.nodelay(True)
    curses.curs_set(0)
    frame_clock = FrameClock()
    running = True

    scene = WorldScene(stdscr)
    while running:
        with frame_clock as next_frame:
            running = scene.handle_input()
            if running:
                scene.update(next_frame)
                _refresh_ui()


def _refresh_ui():
    curses.panel.update_panels()
    curses.doupdate()
