"""Timers and Clocks.

Attributes:
    FPS (constant): target frames per second
"""

from __future__ import annotations

import time
import typing
from contextlib import AbstractContextManager
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from types import TracebackType

FPS: int = 30
_VSYNC = 1.0 / FPS


@dataclass
class FrameData:
    """Data fields related to the current frame.

    All float values are in fractional seconds.
    """
    blown_frames: int = 0
    delta_time: float = 0.0
    frame_left: float = 0.0
    run_time: float = 0.0
    total_frames: int = 0

    @property
    def delta_ms(self) -> float:
        """Get frame delta time in fractional milliseconds instead of
        fractional seconds.
        """
        return self.delta_time * 1000


class FrameClock(AbstractContextManager):
    """A clock controlling the main game loop.

    The frame clock is a context manager where the game is advanced one frame
    each time the clock's runtime context is invoked via the with statement.
    Information about the current frame is the context target provided by
    advancing one tick.
    """

    def __init__(self) -> None:
        """Initialize a frame clock.

        The start time of the first frame and the total runtime is measured
        from the time of this call.
        """
        self._frame = FrameData()
        self._current = 0.0
        self._previous = self._start = time.monotonic()

    def __enter__(self) -> FrameData:
        """Start the current frame.

        Returns:
            The current frame data.
        """
        self._start_frame()
        return self._frame

    def __exit__(self, exc_type: type | None, exc_value: BaseException | None,
                 traceback: TracebackType | None) -> bool:
        """End the current frame.

        Will sleep the main thread if necessary to maintain the target FPS.

        Args:
            exc_type: Raised exception type if any.
            exc_value: Raised exception object if any.
            traceback: Traceback associated with the raised exception if any.

        Returns:
            False, i.e. does not handle any exceptions thrown within the
            runtime context.
        """
        # TODO: should we skip frame end if an exception occurred?
        self._end_frame()
        return False

    def _start_frame(self):
        self._current = time.monotonic()
        # NOTE: cap maximum frame time to 1 second
        self._frame.delta_time = min(self._current - self._previous, 1.0)
        self._frame.run_time = self._current - self._start

    def _end_frame(self):
        self._previous = self._current
        self._frame.total_frames += 1
        frame_elapsed = time.monotonic() - self._current
        # NOTE: we've blown our time budget :( so try to catch up
        if frame_elapsed > _VSYNC:
            self._frame.blown_frames += 1
            return
        self._frame.frame_left = _VSYNC - frame_elapsed
        time.sleep(self._frame.frame_left)
