"""UI abstract and concrete views."""

import abc
import curses
import curses.panel

from terra.codepage import CP437


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
        super().__init__(dim + 4, (dim * 2) + 3, y, x, title='Code Page 437')
        self._draw_codepage(dim)

    def _draw_codepage(self, dim):
        height, width = self._frame.getmaxyx()
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