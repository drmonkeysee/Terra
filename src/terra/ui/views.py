"""UI abstract and concrete views."""

from __future__ import annotations

import abc
import curses
import curses.panel
import typing
from itertools import islice

from terra.codepage import CP437
if typing.TYPE_CHECKING:
    from terra.sim import SimpleMap, Simulation


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
        """Create a new view.

        Must be overridden by subclasses.
        :param h: height of view in cells; if padding is specified this is the
                  height of the view's frame, not the nested content
        :param w: width of view in cells; if padding is specified this is the
                  width of the view's frame, not the nested content
        :param y: y-position of view in screen-space
        :param x: x-position of view in screen-space
        :param padding: padding between view frame and content;
                        if not set then content and frame are the same window
        :param title: optional view title
        """
        self._frame = curses.newwin(h, w, y, x)
        self._frame_panel = curses.panel.new_panel(self._frame)
        self._frame.box()
        self._content, self._content_panel = self._init_content(h, w, padding)
        if title:
            self._set_title(w, title)

    @property
    def content(self) -> curses.window:
        """Get the view's content window."""
        return self._content or self._frame

    def toggle_visibility(self) -> None:
        """Toggle view visibility."""
        if self._frame_panel.hidden():
            self._frame_panel.show()
            if self._content_panel:
                self._content_panel.show()
        else:
            self._frame_panel.hide()
            if self._content_panel:
                self._content_panel.hide()

    def _init_content(self, h, w, padding):
        if not padding:
            return None, None
        adjustment = 2 * padding
        ch, cw = h - adjustment, w - adjustment
        content = self._frame.derwin(ch, cw, padding, padding)
        return content, curses.panel.new_panel(content)

    def _set_title(self, width, title):
        # NOTE: calculate overflow as negative to use directly in slicing
        title_overflow = (width - 2) - len(title)
        if title_overflow < 0:
            title = f'{title[:title_overflow - 1]}…'
        self._frame.addstr(0, 1, title)


class EchoInputView(View):
    """Test view for echoing curses input."""

    def __init__(self, *args: int) -> None:
        """Create echo input view.

        :param *args: size/position parameters passed to parent class
        """
        super().__init__(*args, padding=1)
        self.content.addstr(0, 0, 'Hello from Terra!')
        self.content.move(2, 0)

    def echoch(self, ch: int) -> None:
        """Echo a character to the view's current cursor position."""
        self.content.addch(ch)


class CodePageView(View):
    """Code page 437 display view."""

    def __init__(self, y: int, x: int) -> None:
        """Create code page display view.

        :param y: y-position of view in screen-space
        :param x: x-position of view in screen-space
        """
        # NOTE: 16x16 display
        dim = 16
        height = dim + 4
        width = (dim * 2) + 3
        super().__init__(height, width, y, x, title='Code Page 437')
        self._draw_codepage(dim, height, width)

    def _draw_codepage(self, dim, height, width):
        self.content.addstr(1, 1, '\\')
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
        """Create a simple map view.

        :param *args: size/position parameters passed to parent class
        """
        super().__init__(*args, padding=1, title='Terra')

    def draw_map(self, world_map: SimpleMap) -> None:
        """Draw the map made of the given cells."""
        h, w = self.content.getmaxyx()
        safe_cells = islice(world_map.cells, len(world_map.cells) - 1)
        for i, c in enumerate(safe_cells):
            y, x = divmod(i, w)
            self.content.addstr(y, x, CP437[c])
        # NOTE: last cell (lower-right) must be inserted instead of added to
        # avoid the error thrown by trying to wrap the cursor off the edge
        # of the window.
        self.content.insstr(h - 1, w - 1, CP437[world_map.cells[-1]])


class FrameMetricsView(View):
    """Display frame performance metrics."""

    def __init__(self, y: int, x: int) -> None:
        """Create code page display view.

        :param y: y-position of view in screen-space
        :param x: x-position of view in screen-space
        """
        super().__init__(5, 30, y, x, padding=2, title='Frame Metrics')

    def draw(self, sim: Simulation) -> None:
        self.content.addstr(0, 0, f'Sim value: {sim.sim_value}')


def center_in_win(parent_win: curses.window,
                  h: int, w: int) -> tuple[int, int, int, int]:
    """Calculate y/x coordinates for centering a window of given size within a
    parent window.

    :param parent_win: the parent window in which to center the given
                       dimensions
    :param h: child window height
    :param w: child window width
    :returns: tuple of (height, width, y, x) coordinates centered within
              parent_win
    :raises ValueError: if parent_win is too small to fit the given dimensions
    """
    parent_height, parent_width = parent_win.getmaxyx()
    y, x = (parent_height - h) // 2, (parent_width - w) // 2
    if y < 0 or x < 0:
        raise ValueError('parent window is too small to contain'
                         f' centered window of (h: {h}, w: {w})')
    return h, w, y, x
