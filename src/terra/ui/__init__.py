"""Curses UI layer, including main game/event loop."""

from __future__ import annotations

import curses
import curses.panel
import enum
import time
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


FPS: float = 30.0
VSYNC: float = 1.0 / FPS


class _FrameClock:
    def __init__(self):
        self.current = 0.0
        self.previous = 0.0
        self.elapsed = 0.0

    @property
    def elapsed_ms(self):
        return self.elapsed * 1000

    def start(self):
        self.previous = time.monotonic()

    def tick(self):
        self.current = time.monotonic()
        frametime = self.current - self.previous
        # NOTE: don't let time budget get beyond 1 second
        self.elapsed = max(self.elapsed + frametime, 1.0)

    def sleep(self):
        self.previous = self.current
        frame_elapsed = time.monotonic() - self.current
        # NOTE: we've blown our time budget :( so try to catch up
        if frame_elapsed > VSYNC:
            return
        frame_left = VSYNC - frame_elapsed
        time.sleep(frame_left)


def _main_loop(stdscr, sim):
    stdscr.nodelay(True)
    curses.curs_set(0)

    codepage_view = CodePageView(5, 70)
    codepage_view.toggle_visibility()
    map_view = MapView(*center_in_win(stdscr, 32, 102))
    _new_map(map_view, sim)
    echo_view = EchoInputView(10, 20, 3, 5)
    metrics_view = FrameMetricsView(15, 5)

    frame_clock = _FrameClock()
    frame_clock.start()
    running = True
    while running:
        frame_clock.tick()
        running = _process_input(stdscr, codepage_view, map_view, echo_view,
                                 sim)
        if running:
            sim.update(frame_clock.elapsed_ms)
            _redraw(metrics_view, sim)
        frame_clock.sleep()


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
        case c if c > -1:
            echo_view.echoch(c)
    return True


def _redraw(metrics_view, sim):
    metrics_view.draw(sim)
    curses.panel.update_panels()
    curses.doupdate()


def _new_map(map_view, sim):
    sim.create_map(*map_view.content.getmaxyx())
    map_view.draw_map(sim.world_map)
