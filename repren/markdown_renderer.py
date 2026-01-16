#!/usr/bin/env python
"""
Minimal markdown-to-ANSI renderer with zero dependencies.

Demonstrates how to render basic markdown formatting to terminal
using ANSI escape codes, as inspired by Python 3.14's built-in
argparse color support.

Usage:
    from repren.markdown_renderer import render_markdown
    print(render_markdown("# Hello **world**!"))
"""

import re


# ANSI escape codes
class ANSI:
    """ANSI escape codes for terminal formatting."""

    RESET: str = "\033[0m"
    BOLD: str = "\033[1m"
    DIM: str = "\033[2m"
    ITALIC: str = "\033[3m"
    UNDERLINE: str = "\033[4m"

    # Colors
    BLACK: str = "\033[30m"
    RED: str = "\033[31m"
    GREEN: str = "\033[32m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    MAGENTA: str = "\033[35m"
    CYAN: str = "\033[36m"
    WHITE: str = "\033[37m"

    # Bright colors
    BRIGHT_BLACK: str = "\033[90m"
    BRIGHT_RED: str = "\033[91m"
    BRIGHT_GREEN: str = "\033[92m"
    BRIGHT_YELLOW: str = "\033[93m"
    BRIGHT_BLUE: str = "\033[94m"
    BRIGHT_MAGENTA: str = "\033[95m"
    BRIGHT_CYAN: str = "\033[96m"
    BRIGHT_WHITE: str = "\033[97m"


def render_markdown(text: str, color: bool = True) -> str:
    """
    Render markdown text with ANSI escape codes.

    Supports:
    - Headers (# H1, ## H2, ### H3)
    - Bold (**text** or __text__)
    - Italic (*text* or _text_)
    - Inline code (`code`)
    - Links ([text](url))
    - Lists (- item, * item, 1. item)
    - Code blocks (```language)

    Args:
        text: Markdown text to render
        color: Whether to include ANSI color codes (default: True)

    Returns:
        Text with ANSI formatting codes
    """
    if not color:
        # Strip markdown but don't add ANSI codes
        return _strip_markdown(text)

    lines = text.split("\n")
    result = []
    in_code_block = False

    for line in lines:
        # Code blocks
        if line.startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                # Start of code block
                result.append(f"{ANSI.DIM}───{ANSI.RESET}")
            else:
                # End of code block
                result.append(f"{ANSI.DIM}───{ANSI.RESET}")
            continue

        if in_code_block:
            result.append(f"{ANSI.GREEN}{line}{ANSI.RESET}")
            continue

        # Headers
        if line.startswith("# "):
            formatted = f"{ANSI.BOLD}{ANSI.BRIGHT_BLUE}{line[2:]}{ANSI.RESET}"
            result.append(formatted)
            continue
        elif line.startswith("## "):
            formatted = f"{ANSI.BOLD}{ANSI.BLUE}{line[3:]}{ANSI.RESET}"
            result.append(formatted)
            continue
        elif line.startswith("### "):
            formatted = f"{ANSI.BOLD}{ANSI.CYAN}{line[4:]}{ANSI.RESET}"
            result.append(formatted)
            continue

        # Lists
        if re.match(r"^[-*]\s+", line):
            # Unordered list
            content = re.sub(r"^[-*]\s+", "", line)
            formatted = f"{ANSI.BRIGHT_BLACK}•{ANSI.RESET} {_format_inline(content)}"
            result.append(formatted)
            continue
        elif re.match(r"^\d+\.\s+", line):
            # Ordered list
            match = re.match(r"^(\d+\.)\s+(.*)", line)
            if match:
                num, content = match.groups()
                formatted = f"{ANSI.BRIGHT_BLACK}{num}{ANSI.RESET} {_format_inline(content)}"
                result.append(formatted)
                continue

        # Regular line with inline formatting
        result.append(_format_inline(line))

    return "\n".join(result)


def _format_inline(text: str) -> str:
    """Apply inline formatting (bold, italic, code, links)."""
    # Inline code (do this first to avoid processing markdown inside code)
    text = re.sub(
        r"`([^`]+)`",
        lambda m: f"{ANSI.GREEN}{m.group(1)}{ANSI.RESET}",
        text,
    )

    # Bold (**text** or __text__)
    text = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: f"{ANSI.BOLD}{m.group(1)}{ANSI.RESET}",
        text,
    )
    text = re.sub(
        r"__(.+?)__",
        lambda m: f"{ANSI.BOLD}{m.group(1)}{ANSI.RESET}",
        text,
    )

    # Italic (*text* or _text_) - be careful not to match bold
    text = re.sub(
        r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
        lambda m: f"{ANSI.ITALIC}{m.group(1)}{ANSI.RESET}",
        text,
    )
    text = re.sub(
        r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)",
        lambda m: f"{ANSI.ITALIC}{m.group(1)}{ANSI.RESET}",
        text,
    )

    # Links [text](url) - show as "text (url)" in cyan
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f"{ANSI.CYAN}{m.group(1)}{ANSI.RESET} {ANSI.DIM}({m.group(2)}){ANSI.RESET}",
        text,
    )

    return text


def _strip_markdown(text: str) -> str:
    """Strip markdown formatting without adding ANSI codes."""
    # Headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Code blocks
    text = re.sub(r"```[\w]*\n", "", text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)

    # Italic
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"\1", text)

    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)

    # Lists
    text = re.sub(r"^[-*]\s+", "• ", text, flags=re.MULTILINE)

    return text


if __name__ == "__main__":
    # Demo
    demo_text = """
# Main Heading
This is a paragraph with **bold text**, *italic text*, and `inline code`.

## Subheading
Here's a [link](https://example.com) and more text.

### Features
- First item with **bold**
- Second item with `code`
- Third item

1. Numbered item
2. Another numbered item

```python
def hello():
    print("world")
```

Regular text with all kinds of **formatting** and *styles* combined.
"""

    print("=== Colored Output ===")
    print(render_markdown(demo_text))

    print("\n\n=== Plain Output ===")
    print(render_markdown(demo_text, color=False))
