"""UI abstract and concrete views."""

from __future__ import annotations

import abc
import curses
import curses.panel
import typing
from itertools import islice

from terra.codepage import CP437, MISSING
from terra.ui.clock import FPS

if typing.TYPE_CHECKING:
    from terra.sim import SimpleMap
    from terra.ui.clock import FrameData


class View(abc.ABC):
    """Abstract curses view.

    A view manages a curses window/panel pair of a given size and coordinates;
    the view is always styled with a border to make it visually distinct, and
    can support separating the display frame from window content to allow for
    easier management of content coordinate calculations.

    The abstract view provides flexible initialization and a basic common
    interface; concrete views should inherit from View and provide their own
    initializer and domain-specific interface.
    """

    @abc.abstractmethod
    def __init__(self, h: int, w: int, y: int, x: int, /,
                 *, padding: int = 0, title: str | None = None) -> None:
        """Initialize a new view.

        Must be overridden by subclasses.

        Args:
            h: height of view in cells; if padding is specified this is the
               height of the view's frame, not the nested content.
            w: width of view in cells; if padding is specified this is the
               width of the view's frame, not the nested content.
            y: y-position of view in screen-space.
            x: x-position of view in screen-space.
            padding: padding between view frame and content;
                     if not set then content and frame are the same window.
            title: optional view title.

        Attributes:
            frame: the view's frame window.
        """
        self.frame = curses.newwin(h, w, y, x)
        self.frame_panel = curses.panel.new_panel(self.frame)
        self.frame.box()
        self._content, self._content_panel = self._init_content(h, w, padding)
        if title:
            self._set_title(w, title)

    @property
    def content(self) -> curses.window:
        """Get the view's content window."""
        return self._content or self.frame

    def toggle_visibility(self) -> None:
        """Toggle view visibility."""
        if self.frame_panel.hidden():
            self.frame_panel.show()
            if self._content_panel:
                self._content_panel.show()
        else:
            if self._content_panel:
                self._content_panel.hide()
            self.frame_panel.hide()

    def _init_content(self, h, w, padding):
        if not padding:
            return None, None
        adjustment = 2 * padding
        ch, cw = h - adjustment, w - adjustment
        content = self.frame.derwin(ch, cw, padding, padding)
        return content, curses.panel.new_panel(content)

    def _set_title(self, width, title):
        # NOTE: calculate overflow as negative to use directly in slicing
        title_overflow = (width - 2) - len(title)
        if title_overflow < 0:
            title = f'{title[:title_overflow - 1]}…'
        self.frame.addstr(0, 1, title)


class CodePageView(View):
    """Code page 437 display view."""

    def __init__(self, y: int, x: int) -> None:
        """Initialize code page display view.

        Args:
            y: y-position of view in screen-space.
            x: x-position of view in screen-space.
        """
        dim = 16
        height = dim + 4
        width = (dim * 2) + 3
        super().__init__(height, width, y, x, title='Code Page 437')
        self._draw_codepage(dim, height, width)

    def _draw_codepage(self, dim, height, width):
        self.content.addstr(1, 1, MISSING)
        self.content.hline(2, 1, 0, width - 2)
        self.content.vline(1, 2, 0, height - 2)
        self.content.addch(2, 0, curses.ACS_LTEE)
        self.content.addch(2, 2, curses.ACS_PLUS)
        self.content.addch(2, width - 1, curses.ACS_RTEE)
        self.content.addch(height - 1, 2, curses.ACS_BTEE)
        grid_pad = 3
        for i in range(dim):
            self.content.addstr(1, (i * 2) + grid_pad, f'{i:X}')
        for i, c in enumerate(CP437):
            y, x = divmod(i, dim)
            self.content.addstr(y + grid_pad, 1, f'{y:X}')
            self.content.addstr(y + grid_pad, (x * 2) + grid_pad, c)


class MapView(View):
    """Display simple map view."""

    def __init__(self, *args: int) -> None:
        """Initialize a simple map view.

        Args:
            *args: size/position parameters passed to parent class.
        """
        super().__init__(*args, padding=1, title='Terra')

    def redraw(self, world_map: list[int]) -> None:
        """Draw the map made of the given cells."""
        h, w = self.content.getmaxyx()
        safe_cells = islice(world_map, len(world_map) - 1)
        for i, c in enumerate(safe_cells):
            y, x = divmod(i, w)
            self.content.addstr(y, x, CP437[c])
        # NOTE: last cell (lower-right) must be inserted instead of added to
        # avoid the error thrown by trying to wrap the cursor off the edge
        # of the window.
        self.content.insstr(h - 1, w - 1, CP437[world_map[-1]])


class FrameMetricsView(View):
    """Display frame performance metrics."""
    # NOTE: refresh delta-t every quarter second for easier readability
    _DT_REFRESH_INTERVAL = 0.25
    _MIN_WIDTH = 28

    def __init__(self, w: int, y: int, x: int) -> None:
        """Initialize frame performance view.

        Args:
            w: width of the view in cells; may be adjusted to a minimum
               threshold if the given value is too small to fit content.
            y: y-position of view in screen-space.
            x: x-position of view in screen-space.
        """
        super().__init__(8, max(self._MIN_WIDTH, w), y, x,
                         padding=2, title='Frame Metrics')
        self._display_dt = self._display_frame_left = self._refresh_dt = 0

    def redraw(self, frame: FrameData) -> None:
        """Refresh view with the latest frame stats."""
        self._update_delta_t(frame)
        self.content.addstr(0, 0, f'FPS: {FPS}')
        self.content.addstr(1, 0,
                            f'Frames: {frame.total_frames}'
                            f' ({frame.blown_frames})')
        self.content.addstr(2, 0,
                            f'ΔT: {self._display_dt * 1000:.3f}'
                            f' ({self._display_frame_left * 1000:+.3f})')
        self.content.addstr(3, 0, f'Runtime: {frame.run_time:.3f}')

    def _update_delta_t(self, frame):
        self._refresh_dt += frame.delta_time
        if self._refresh_dt >= self._DT_REFRESH_INTERVAL:
            self._display_dt = frame.delta_time
            self._display_frame_left = frame.frame_left
            self._refresh_dt = 0
