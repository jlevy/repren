"""
Readable argparse utilities for colorized help with rich_argparse.

This module provides a formatter for argparse that uses rich for colorization
and improves readability with better formatting and console width handling.
"""

from typing import Any

import rich_argparse._lazy_rich as r
from rich import get_console
from rich_argparse.contrib import ParagraphRichHelpFormatter
from typing_extensions import override


def get_readable_console_width(min_width: int = 40, max_width: int = 100) -> int:
    """
    Get a readable console width by default between 40 and 100 characters.
    Very wide consoles are common but not readable for long text.
    """
    return max(min_width, min(max_width, get_console().width))


class ReadableColorFormatter(ParagraphRichHelpFormatter):
    """
    A formatter for `argparse` that colorizes with `rich_argparse` and makes a
    few other small changes to improve readability.

    - Preserves paragraphs, unlike the default argparse formatters.
    - Wraps text to console width but with a max width of 100 characters, which
      is better for readability in both wide and narrow consoles.
    - Adds a newline after each action for better readability.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        width = get_readable_console_width()
        super().__init__(*args, width=width, **kwargs)

        # This is a bit of a hack but lets us control formatting.
        # Define our own _Section class that inherits from the parent's _Section.
        # This is only needed to slightly adjust the layout: in particular to add a
        # newline after each subcommand description for better readability.
        class _Section(ParagraphRichHelpFormatter._Section):  # pyright: ignore[reportPrivateUsage]
            @override
            def _render_actions(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
                if not self.rich_actions:
                    return
                options = options.update(no_wrap=True, overflow="ignore")
                help_pos = min(self.formatter._action_max_length + 2, self.formatter._max_help_position)
                help_width = max(self.formatter._width - help_pos, 11)
                indent = r.Text(" " * help_pos)
                # New variables for our feature
                new_line = r.Segment.line()
                num_actions = len(self.rich_actions)

                # Use enumerate to get the index
                for i, (action_header, action_help) in enumerate(self.rich_actions):
                    if not action_help:
                        # no help, yield the header and finish
                        yield from console.render(action_header, options)
                        # We remove the 'continue' to allow adding newlines after each item
                    else:
                        action_help_lines = self.formatter._rich_split_lines(action_help, help_width)  # pyright: ignore[reportPrivateUsage]
                        if len(action_header) > help_pos - 2:
                            # the header is too long, put it on its own line
                            yield from console.render(action_header, options)
                            action_header = indent
                            action_header.set_length(help_pos)
                            action_help_lines[0].rstrip()
                            yield from console.render(action_header + action_help_lines[0], options)
                            for line in action_help_lines[1:]:
                                line.rstrip()
                                yield from console.render(indent + line, options)

                    # Here's our only functional change - add newline if not the last item
                    if i < num_actions - 1:
                        yield new_line

                yield ""

        self._Section = _Section  # pyright: ignore[reportPrivateUsage]
