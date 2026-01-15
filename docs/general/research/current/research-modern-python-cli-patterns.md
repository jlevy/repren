# Research Brief: Modern Python CLI Architecture Patterns

**Last Updated**: 2025-01-14

**Status**: Complete

**Related**:

- [Modern TypeScript CLI Patterns](research-modern-typescript-cli-patterns.md) —
  Equivalent patterns for TypeScript/Node.js CLIs

- [Typer Documentation](https://typer.tiangolo.com/) — Modern CLI framework

- [Rich Documentation](https://rich.readthedocs.io/) — Terminal formatting

- [uv Documentation](https://docs.astral.sh/uv/) — Modern Python package manager

- [simple-modern-uv Template](https://github.com/jlevy/simple-modern-uv) — Modern Python
  project template

* * *

## Executive Summary

This research brief documents proven architectural patterns for building maintainable
Python CLI applications using modern tooling (Typer, Rich, uv).
These patterns address common challenges: code duplication across commands, dual output
modes (human-readable vs machine-parseable), consistent error handling, and testability.

The recommended architecture uses a **Base Command pattern** with an **OutputManager**
for dual-mode output, **Handler separation** for clean organization, and **uv-based
versioning** for accurate version strings.

**Research Questions**:

1. How should CLI commands be structured to minimize code duplication?

2. What patterns support both human-readable and JSON output modes?

3. How should version information be derived for CLI tools?

4. What directory structure best organizes CLI code in a library/CLI hybrid package?

* * *

## Research Methodology

### Approach

Patterns were extracted from production Python CLI tools, analyzed for common solutions
to recurring problems, and documented with complete implementation examples.

### Sources

- Production CLI implementations using Typer and Rich

- [simple-modern-uv](https://github.com/jlevy/simple-modern-uv) project template

- [uvtemplate](https://github.com/jlevy/uvtemplate) CLI implementation

- Unix philosophy for output handling (stdout vs stderr)

- PEP standards for versioning and packaging

* * *

## Research Findings

### 1. Directory Structure

**Status**: Recommended

**Details**:

Use the `src` layout for maintainability with clear separation between commands, shared
utilities, and type definitions:

```
src/myproject/
├── __init__.py             # Package entry, VERSION export
├── cli.py                  # Main entry point, app setup
├── commands/               # Command implementations
│   ├── __init__.py
│   ├── my_feature.py       # Command with subcommands
│   └── simple_cmd.py       # Simple single command
├── lib/                    # Shared utilities and base classes
│   ├── __init__.py
│   ├── base_command.py     # Base class for handlers
│   ├── output_manager.py   # Unified output handling
│   ├── context.py          # Global option management
│   ├── formatters.py       # Domain-specific formatters
│   └── utils.py            # General utilities
└── types/
    ├── __init__.py
    └── options.py          # TypedDict for command options
```

**Assessment**: This structure scales well from small CLIs to large ones with many
commands. The `lib/` directory prevents code duplication, while `types/` keeps type
definitions organized.
The `src` layout prevents import confusion during development.

* * *

### 2. Agent & CI Compatibility

**Status**: Strongly Recommended

**Details**:

Modern CLIs must work reliably in three execution contexts:

| Mode | Context | Behavior |
| --- | --- | --- |
| **Interactive (TTY)** | Human at terminal | Prompts, spinners, colored output allowed |
| **Non-interactive (headless)** | CI, scripts, agent runners | No prompts, deterministic output, fail-fast |
| **Protocol mode** | MCP/JSON-RPC adapters | Structured I/O only (future extension) |

**Key flags for automation**:

```python
@app.callback()
def main(
    ctx: typer.Context,
    non_interactive: Annotated[
        bool, typer.Option("--non-interactive", help="Disable prompts, fail if input required")
    ] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Assume yes to confirmations")] = False,
    format: Annotated[str, typer.Option(help="Output format: text, json, or jsonl")] = "text",
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["non_interactive"] = non_interactive or not sys.stdin.isatty()
    ctx.obj["yes"] = yes
    ctx.obj["format"] = format
```

**Behavior contract**:

- If `--non-interactive` is set, stdin is not a TTY, or `CI` env var is set, **never
  prompt**

- If required values are missing, exit with code `2` and an actionable error:

```python
from .exceptions import ValidationError

def require_input(value: str | None, field: str, ctx: dict) -> str:
    """Get required input, failing in non-interactive mode if missing."""
    if value:
        return value
    if ctx.get("non_interactive") or not sys.stdin.isatty():
        raise ValidationError(
            f"Missing required input: {field}",
            hint=f"Provide --{field} or run interactively",
        )
    return questionary.text(f"{field}:").ask() or ""
```

- `--yes` skips confirmations but does **not** conjure missing required fields

- Respect `CI` environment variable (set by GitHub Actions, GitLab CI, CircleCI, Travis,
  and most CI systems):

```python
import os

def is_ci() -> bool:
    return bool(os.environ.get("CI"))

def is_interactive() -> bool:
    return sys.stdin.isatty() and not is_ci()
```

- Support `NO_COLOR` environment variable (see [no-color.org](https://no-color.org/))

**Self-documentation for agents** (optional but high-value):

```python
@app.command("schema")
def schema_command(command_name: str) -> None:
    """Output JSON Schema for command inputs."""
    schema = get_command_schema(command_name)
    print(json.dumps(schema, indent=2))

@app.command("examples")
def examples_command(command_name: str) -> None:
    """Output example invocations as JSON."""
    examples = get_command_examples(command_name)
    print(json.dumps(examples, indent=2))
```

**Critical: Disable spinners and progress output for agents**

Spinners and progress indicators are a severe antipattern in non-interactive contexts.
When an AI coding agent (Claude Code, Cursor, Copilot, etc.)
invokes a CLI, any spinner output—even partial line rewrites via ANSI escape codes—gets
captured as text and floods the agent’s context window.
A single long-running command with an active spinner can generate thousands of lines of
captured output, rapidly exhausting context and degrading agent performance.

```python
# ALWAYS check TTY before showing progress
if not sys.stderr.isatty():
    # No spinners, no progress bars, no animations
    pass

# Provide explicit flag for agent-driven invocations
@app.callback()
def main(
    no_progress: Annotated[
        bool, typer.Option("--no-progress", help="Disable progress output (for agent/script use)")
    ] = False,
) -> None:
    ctx.obj["no_progress"] = no_progress

# In OutputManager, respect both TTY detection AND explicit flag
def spinner(self, message: str) -> Progress | None:
    if self.no_progress or not sys.stderr.isatty():
        return None  # Silent no-op
    # ...create actual spinner
```

Key requirements:

- **Always check `isatty()`** before any spinner/progress output

- **Provide `--no-progress` flag** for explicit disabling (agents may run in
  pseudo-TTYs)

- **Default to silent** when in doubt—missing progress output is far better than flooded
  context

- **Never use carriage returns (`\r`) or ANSI cursor movement** in non-TTY mode

**Assessment**: Explicit automation support enables CLIs to work reliably with AI
agents, CI pipelines, and scripted workflows without TTY hacks or brittle parsing.

* * *

### 3. Modern Tooling Stack

**Status**: Strongly Recommended

**Details**:

Use this modern tooling stack for Python CLI development:

| Tool | Purpose | Can Replace |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | Package management, venvs, Python versions | pip, poetry, pyenv, virtualenv (in most workflows) |
| [Rich](https://rich.readthedocs.io/) | Terminal output, tables, progress | colorama, tabulate |
| [Ruff](https://docs.astral.sh/ruff/) | Linting and formatting | black, flake8, isort |
| [BasedPyright](https://docs.basedpyright.com/) | Type checking | mypy |
| [pytest](https://docs.pytest.org/) | Testing | unittest |

**CLI Framework Choice:**

Two modern approaches for CLI parsing, both integrating well with Rich:

| Approach | Best For | Trade-offs |
| --- | --- | --- |
| **[argparse](https://docs.python.org/3/library/argparse.html) + [rich_argparse](https://github.com/hamdanal/rich_argparse)** | Traditional CLIs, straightforward options | Simple, minimal, stdlib-based; more explicit |
| **[Typer](https://typer.tiangolo.com/)** | Complex CLIs, type-hint enthusiasts | Modern API, automatic features; more opinionated |

**Option A: argparse + rich_argparse (Simple and traditional)**

For many CLIs, argparse with rich_argparse provides a cleaner, more traditional
approach. It’s less opinionated and works well when you want straightforward option
configuration. See
[clideps readable_argparse.py](https://github.com/jlevy/clideps/blob/main/src/clideps/utils/readable_argparse.py)
for an enhanced formatter with better readability:

```python
from argparse import ArgumentParser
from rich_argparse import RichHelpFormatter

parser = ArgumentParser(
    description="My CLI tool",
    formatter_class=RichHelpFormatter,
)
parser.add_argument("name", help="Name to greet")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
args = parser.parse_args()
```

**Note**: Prefer long option names (e.g., `--verbose`) over single-letter aliases (e.g.,
`-v`) in new CLIs to avoid conflicts.
Single-letter aliases are acceptable when maintaining backward compatibility with
existing tools.

For enhanced readability (paragraph preservation, markdown support, smart width):

```python
# Using ReadableColorFormatter pattern from clideps
from rich_argparse import ParagraphRichHelpFormatter
import shutil

class ReadableColorFormatter(ParagraphRichHelpFormatter):
    """Enhanced formatter with better spacing and markdown support."""

    def __init__(self, prog: str, max_width: int = 100) -> None:
        # Clamp width between 40-100 for readability
        width = min(max_width, max(40, shutil.get_terminal_size().columns))
        super().__init__(prog, max_help_position=40, width=width)
```

**Option B: Typer (Modern, type-hint based)**

Typer provides a more opinionated, type-hint-based API with automatic features:

```python
from typing import Annotated
import typer

app = typer.Typer()

@app.command()
def greet(name: Annotated[str, typer.Argument(help="Name to greet")]) -> None:
    """Greet someone by name."""
    print(f"Hello, {name}!")
```

**pyproject.toml configuration** (argparse + rich_argparse approach):

```toml
[project]
dependencies = [
    "rich>=14.0.0",
    "rich-argparse>=1.7.0",
]

[project.scripts]
my-cli = "myproject.cli:main"
```

**pyproject.toml configuration** (Typer approach):

```toml
[build-system]
requires = ["hatchling", "uv-dynamic-versioning"]
build-backend = "hatchling.build"

[project]
name = "my-cli"
dynamic = ["version"]
requires-python = ">=3.11"
dependencies = [
    "typer>=0.15.0",
    "rich>=14.0.0",
]

[project.scripts]
my-cli = "myproject.cli:app"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-sugar>=1.0.0",
    "ruff>=0.9.0",
    "basedpyright>=1.29.0",
]

[tool.uv-dynamic-versioning]
enable = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "UP", "B", "I"]

[tool.basedpyright]
typeCheckingMode = "strict"
```

**Assessment**: Both approaches are valid for modern Python CLI development.
argparse + rich_argparse is simpler, more traditional, and works well for
straightforward CLIs with standard options.
Typer is more opinionated but provides automatic features that can reduce boilerplate
for complex CLIs with many commands.

* * *

### 4. Base Command Pattern

**Status**: Strongly Recommended

**Details**:

Use a base class to eliminate duplicate code across commands.
This pattern centralizes:

- Context extraction from Typer’s context

- Output management initialization

- Client/API connection handling

- Error handling with consistent formatting

- Dry-run checking

```python
# lib/base_command.py
from typing import TypeVar, Callable, Any
from typer import Context
from .output_manager import OutputManager, OutputFormat
from .context import CommandContext, get_command_context
from .exceptions import CLIError

T = TypeVar("T")


class BaseCommand:
    """Base class for command handlers with common functionality."""

    def __init__(self, ctx: Context, format: OutputFormat = "text") -> None:
        self.ctx = get_command_context(ctx)
        self.output = OutputManager(format=format, **self.ctx)
        self._client: HttpClient | None = None

    def get_client(self) -> HttpClient:
        """Lazy-initialize HTTP client."""
        if self._client is None:
            self._client = HttpClient(get_api_url())
        return self._client

    def execute(
        self,
        action: Callable[[], T],
        error_message: str,
    ) -> T:
        """Execute action with consistent error handling.

        Raises CLIError instead of SystemExit - exit handled at entrypoint.
        """
        try:
            return action()
        except CLIError:
            raise  # Re-raise CLI errors as-is
        except Exception as e:
            self.output.error(error_message, e)
            raise CLIError(error_message) from e

    def check_dry_run(self, message: str, details: dict[str, Any] | None = None) -> bool:
        """Check if in dry-run mode and log accordingly."""
        if self.ctx.dry_run:
            self.output.dry_run(message, details)
            return True
        return False


# Usage in command handler:
class MyCommandHandler(BaseCommand):
    def run(self, name: str, limit: int) -> None:
        if self.check_dry_run("Would perform action", {"name": name}):
            return

        client = self.get_client()
        result = self.execute(
            lambda: client.query({"name": name, "limit": limit}),
            "Failed to fetch data",
        )

        self.output.data(result, lambda: display_result(result, self.ctx))
```

**CLI entrypoint** (single place for exit handling):

```python
# cli.py
import signal
import typer
from .exceptions import CLIError, UserCancelled

app = typer.Typer()

def main() -> None:
    """CLI entrypoint with centralized error handling."""
    try:
        app()
    except UserCancelled as e:
        # User cancelled - not an error
        raise typer.Exit(e.exit_code)
    except CLIError as e:
        # All CLI errors handled here
        raise typer.Exit(e.exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        raise typer.Exit(130)  # 128 + SIGINT(2)

if __name__ == "__main__":
    main()
```

**Assessment**: The Base Command pattern dramatically reduces boilerplate.
New commands inherit consistent behavior for error handling, dry-run support, and output
formatting. Throwing `CLIError` instead of calling `sys.exit()` or `raise SystemExit()`
improves testability and ensures proper resource cleanup.

* * *

### 5. Dual Output Mode (Text + JSON)

**Status**: Strongly Recommended

**Details**:

Support both human-readable and machine-parseable output through an OutputManager class
that handles format switching transparently:

```python
# lib/output_manager.py
from typing import Literal, TypeVar, Callable, Any
import json
import os
import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

OutputFormat = Literal["text", "json", "jsonl"]
ColorOption = Literal["auto", "always", "never"]
T = TypeVar("T")


def _create_console(color: ColorOption, stderr: bool = False) -> Console:
    """Create a Rich Console with appropriate color settings."""
    # Respect NO_COLOR env var (https://no-color.org/)
    no_color = bool(os.environ.get("NO_COLOR")) and color != "always"
    force_terminal = color == "always"
    return Console(
        stderr=stderr,
        force_terminal=force_terminal,
        no_color=no_color or color == "never",
    )


class OutputManager:
    """Unified output handling for dual-mode CLI output."""

    def __init__(
        self,
        format: OutputFormat = "text",
        color: ColorOption = "auto",
        quiet: bool = False,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        self.format = format
        self.quiet = quiet
        self.verbose = verbose
        self._console = _create_console(color)
        self._err_console = _create_console(color, stderr=True)

    def data(self, data: T, text_formatter: Callable[[T], None] | None = None) -> None:
        """Output structured data - always goes to stdout."""
        if self.format == "json":
            print(json.dumps(data, indent=2, default=str))
        elif self.format == "jsonl":
            print(json.dumps({"type": "result", "data": data}, default=str))
        elif text_formatter:
            text_formatter(data)

    def success(self, message: str) -> None:
        """Status messages - text mode only, stdout."""
        if self.format == "text" and not self.quiet:
            self._console.print(f"[green]✓[/green] {message}")

    def info(self, message: str) -> None:
        """Info messages - text mode only, stdout."""
        if self.format == "text" and not self.quiet:
            self._console.print(f"[blue]ℹ[/blue] {message}")

    def warning(self, message: str) -> None:
        """Warnings - always stderr, always shown."""
        if self.format in ("json", "jsonl"):
            print(json.dumps({"type": "warning", "message": message}), file=sys.stderr)
        else:
            self._err_console.print(f"[yellow]⚠[/yellow] {message}")

    def error(self, message: str, err: Exception | None = None) -> None:
        """Errors - always stderr, always shown."""
        if self.format in ("json", "jsonl"):
            error_data: dict[str, Any] = {"type": "error", "message": message}
            if err:
                error_data["details"] = str(err)
            print(json.dumps(error_data), file=sys.stderr)
        else:
            self._err_console.print(f"[red]✗[/red] Error: {message}")
            if err and self.verbose:
                self._err_console.print(f"  [dim]{err}[/dim]")

    def dry_run(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Dry-run output - shows what would be done."""
        if self.format in ("json", "jsonl"):
            print(json.dumps({"type": "dry_run", "message": message, "details": details}))
        else:
            self._console.print(f"[cyan]DRY-RUN:[/cyan] {message}")
            if details:
                for key, value in details.items():
                    self._console.print(f"  [dim]{key}:[/dim] {value}")

    def spinner(self, message: str) -> Progress | None:
        """Spinner - returns None in JSON/quiet mode or non-TTY.

        Spinners go to stderr to keep stdout clean for pipeable data.
        """
        if self.format == "text" and not self.quiet and sys.stderr.isatty():
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self._err_console,  # Use stderr for spinners
                transient=True,  # Don't leave artifacts
            )
            progress.add_task(message, total=None)
            return progress
        return None
```

**Key principles**:

| Output Type | Destination | When Shown |
| --- | --- | --- |
| Data (results) | stdout | Always |
| Success messages | stdout | Text mode, not quiet |
| Errors | stderr | Always |
| Warnings | stderr | Always |
| Spinners/progress | stderr | Text mode, TTY only |

**Note**: Spinners and progress indicators go to **stderr** to keep stdout clean for
pipeable data. Disable them entirely when stderr is not a TTY (prevents corruption in
`my-cli list | jq ...` scenarios).

**Assessment**: This pattern enables Unix pipeline compatibility
(`my-cli list --format json | jq '.items[]'`) while providing rich interactive output
for terminal users.

* * *

### 6. Handler + Command Structure

**Status**: Recommended

**Details**:

Separate command definitions from implementation for cleaner code organization:

```python
# commands/my_feature.py
from typing import Annotated
import typer
from ..lib.base_command import BaseCommand
from ..lib.output_manager import OutputFormat
from ..lib.context import get_command_context

app = typer.Typer(help="Manage resources")


class MyFeatureListHandler(BaseCommand):
    """Handler for listing resources."""

    def run(self, limit: int, status: str | None) -> None:
        client = self.get_client()
        items = self.execute(
            lambda: client.list_items(limit=limit, status=status),
            "Failed to list items",
        )
        self.output.data(
            format_items_json(items),
            lambda: display_items(items, self.ctx),
        )


@app.command("list")
def list_command(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option(help="Maximum results")] = 20,
    status: Annotated[str | None, typer.Option(help="Filter by status")] = None,
    format: Annotated[OutputFormat, typer.Option(help="Output format")] = "text",
) -> None:
    """List resources."""
    handler = MyFeatureListHandler(ctx, format)
    handler.run(limit, status)


@app.command("show")
def show_command(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="Resource ID")],
    format: Annotated[OutputFormat, typer.Option(help="Output format")] = "text",
) -> None:
    """Show a specific resource."""
    handler = MyFeatureShowHandler(ctx, format)
    handler.run(id)
```

**Assessment**: This separation keeps command registration concise while allowing
complex handler logic.
The handler class is testable in isolation.

* * *

### 7. Typed Options with TypedDict

**Status**: Recommended

**Details**:

Use TypedDict for command options to get TypeScript-like type safety:

```python
# types/options.py
from typing import TypedDict, NotRequired


class MyFeatureListOptions(TypedDict):
    limit: int
    status: NotRequired[str | None]
    verbose: bool


class MyFeatureCreateOptions(TypedDict):
    name: str
    description: NotRequired[str | None]


# Usage in handler:
class MyFeatureListHandler(BaseCommand):
    def run(self, options: MyFeatureListOptions) -> None:
        limit = options["limit"]
        # TypedDict provides autocomplete and type checking
```

**Alternative: dataclasses**:

```python
from dataclasses import dataclass


@dataclass
class MyFeatureListOptions:
    limit: int = 20
    status: str | None = None
    verbose: bool = False
```

**Assessment**: TypedDict or dataclasses catch errors at type-check time and provide
autocomplete in editors.
Worth the small overhead of maintaining definitions.

* * *

### 8. Formatter Pattern

**Status**: Recommended

**Details**:

Pair text and JSON formatters for each domain.
Text formatters handle human-readable display; JSON formatters structure data for
machine consumption:

```python
# lib/formatters.py
from rich.console import Console
from rich.table import Table
from typing import Any

console = Console()


def display_items(items: list[dict[str, Any]], ctx: dict[str, Any]) -> None:
    """Text formatter - for human-readable output."""
    if not items:
        console.print("[dim]No items found[/dim]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Status")

    for item in items:
        status_style = "green" if item["status"] == "active" else "yellow"
        table.add_row(
            item["id"],
            item["name"],
            f"[{status_style}]{item['status']}[/{status_style}]",
        )

    console.print(table)


def format_items_json(items: list[dict[str, Any]]) -> dict[str, Any]:
    """JSON formatter - structured data for machine consumption."""
    return {
        "total": len(items),
        "items": [
            {
                "id": item["id"],
                "name": item["name"],
                "status": item["status"],
            }
            for item in items
        ],
    }


# Usage in handler:
self.output.data(
    format_items_json(items),  # JSON format
    lambda: display_items(items, self.ctx),  # Text format
)
```

**Assessment**: Separating formatters makes them reusable and testable.
The JSON formatter defines the contract for machine consumers.

* * *

### 9. Version Handling

**Status**: Recommended

**Details**:

Use dynamic git-based versioning via `uv-dynamic-versioning` for accurate version
strings without manual updates:

**pyproject.toml configuration**:

```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
source = "uv-dynamic-versioning"

[tool.uv-dynamic-versioning]
enable = true
```

**CLI integration**:

```python
# __init__.py
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("my-cli")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

# cli.py
from . import __version__

app = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        print(f"my-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """My CLI tool."""
    pass
```

**Key points**:

- Use `importlib.metadata.version()` for runtime version lookup

- Version is derived from git tags (e.g., `v1.2.3` → `1.2.3`)

- Between releases: `1.2.3+g1234abc` format shows commit hash

- No manual version bumping required

**Assessment**: Git-based versioning eliminates version drift between git tags and
package metadata. The version is always accurate.

* * *

### 10. Global Options

**Status**: Recommended

**Details**:

Define global options once at the app level using Typer’s callback:

```python
# cli.py
from typing import Annotated, Literal
import sys
import typer
from .lib.context import set_global_context

app = typer.Typer()

ColorOption = Literal["auto", "always", "never"]


@app.callback()
def main(
    ctx: typer.Context,
    dry_run: Annotated[bool, typer.Option(help="Show what would be done")] = False,
    verbose: Annotated[bool, typer.Option(help="Enable verbose output")] = False,
    quiet: Annotated[bool, typer.Option(help="Suppress non-essential output")] = False,
    format: Annotated[str, typer.Option(help="Output format: text, json, or jsonl")] = "text",
    color: Annotated[ColorOption, typer.Option(help="Colorize output: auto, always, never")] = "auto",
    non_interactive: Annotated[bool, typer.Option("--non-interactive", help="Disable prompts")] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Assume yes to confirmations")] = False,
) -> None:
    """My CLI tool for managing resources."""
    ctx.ensure_object(dict)
    is_ci = bool(os.environ.get("CI"))
    ctx.obj["dry_run"] = dry_run
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["format"] = format
    ctx.obj["color"] = color
    ctx.obj["non_interactive"] = non_interactive or not sys.stdin.isatty() or is_ci
    ctx.obj["yes"] = yes


# Access in commands via context:
def get_command_context(ctx: typer.Context) -> dict[str, Any]:
    """Extract global options from Typer context."""
    obj = ctx.ensure_object(dict)
    return {
        "dry_run": obj.get("dry_run", False),
        "verbose": obj.get("verbose", False),
        "quiet": obj.get("quiet", False),
        "format": obj.get("format", "text"),
        "color": obj.get("color", "auto"),
        "non_interactive": obj.get("non_interactive", False),
        "yes": obj.get("yes", False),
    }
```

**Color output handling:**

The `--color` option follows the Unix convention used by `git`, `ls`, `grep`:

- `auto` (default): Enable colors when stdout is a TTY, disable when piped/redirected

- `always`: Force colors (useful for `less -R` or capturing colored output)

- `never`: Disable colors entirely

Also respect the `NO_COLOR` environment variable (see
[no-color.org](https://no-color.org/)):

```python
# lib/colors.py
import os
import sys
from typing import Literal

ColorOption = Literal["auto", "always", "never"]


def should_colorize(color_option: ColorOption) -> bool:
    """Determine if output should be colorized based on --color option and NO_COLOR."""
    # NO_COLOR takes precedence (unless --color=always explicitly set)
    if os.environ.get("NO_COLOR") and color_option != "always":
        return False
    if color_option == "always":
        return True
    if color_option == "never":
        return False
    return sys.stdout.isatty()


# Rich integration - pass to Console:
from rich.console import Console

def create_console(color_option: ColorOption, stderr: bool = False) -> Console:
    """Create a Rich Console with appropriate color settings."""
    no_color_env = bool(os.environ.get("NO_COLOR")) and color_option != "always"
    force_terminal = color_option == "always"
    no_color = color_option == "never" or no_color_env
    return Console(stderr=stderr, force_terminal=force_terminal, no_color=no_color)
```

**Alternative: `--json` flag:**

Some CLIs use a simpler `--json` boolean flag instead of `--format`. This is less
extensible but more concise for the common case:

```python
json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False
```

**Assessment**: Centralizing global options ensures consistency and prevents option name
conflicts across commands.

* * *

### 11. Rich Output Utilities

**Status**: Recommended

**Details**:

Create a utilities module for consistent Rich output patterns:

```python
# lib/rich_utils.py
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Any

console = Console()
err_console = Console(stderr=True)


def print_success(message: str) -> None:
    """Print success message with green checkmark."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message to stderr."""
    err_console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message to stderr."""
    err_console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_subtle(message: str) -> None:
    """Print dimmed text for less important info."""
    console.print(f"[dim]{message}[/dim]")


def create_table(columns: list[str], title: str | None = None) -> Table:
    """Create a standard table with consistent styling."""
    table = Table(title=title, show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)
    return table


def show_json(data: Any, title: str | None = None) -> None:
    """Display JSON with syntax highlighting."""
    import json
    json_str = json.dumps(data, indent=2, default=str)
    syntax = Syntax(json_str, "json", theme="monokai")
    if title:
        console.print(Panel(syntax, title=title))
    else:
        console.print(syntax)


def spinner_context(message: str):
    """Context manager for spinner during long operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )
```

**Assessment**: Centralizing Rich utilities ensures consistent styling across all
commands and makes it easy to update the visual style in one place.

* * *

### 12. Stdout/Stderr Separation

**Status**: Essential

**Details**:

Route output appropriately for Unix pipeline compatibility:

```python
import sys
from rich.console import Console

# Separate consoles for stdout and stderr
console = Console()  # stdout
err_console = Console(stderr=True)  # stderr


def output_data(data: dict) -> None:
    """Data/results → stdout (can be piped)."""
    import json
    print(json.dumps(data, indent=2))


def output_success(message: str) -> None:
    """Success messages → stdout."""
    console.print(f"[green]✓[/green] {message}")


def output_error(message: str) -> None:
    """Errors → stderr (visible even when piped)."""
    err_console.print(f"[red]✗[/red] Error: {message}")


def output_warning(message: str) -> None:
    """Warnings → stderr."""
    err_console.print(f"[yellow]⚠[/yellow] {message}")


# This enables: my-cli list --format json | jq '.items[]'
```

**Assessment**: Proper stdout/stderr separation is fundamental to Unix philosophy and
enables CLI tools to be composed in pipelines.

* * *

### 13. Error Handling with Custom Exceptions

**Status**: Recommended

**Details**:

Define custom exceptions for different failure modes:

```python
# lib/exceptions.py
class CLIError(Exception):
    """Base exception for CLI errors."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class UserCancelled(CLIError):
    """User cancelled the operation."""

    def __init__(self, message: str = "Operation cancelled") -> None:
        super().__init__(message, exit_code=0)


class ValidationError(CLIError):
    """Input validation failed."""

    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=2)


class APIError(CLIError):
    """API request failed."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message, exit_code=1)


# Usage in CLI entry point:
@app.command()
def my_command(ctx: typer.Context) -> None:
    try:
        handler = MyHandler(ctx)
        handler.run()
    except UserCancelled as e:
        output.info(e.message)
        raise typer.Exit(e.exit_code)
    except CLIError as e:
        output.error(e.message)
        raise typer.Exit(e.exit_code)
    except KeyboardInterrupt:
        output.info("Interrupted")
        raise typer.Exit(130)  # Standard exit code for SIGINT
```

**Exit code conventions**:

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | General error |
| 2 | Invalid usage / validation error |
| 130 | Interrupted (Ctrl+C) |

**Assessment**: Custom exceptions make error handling explicit and testable.
Exit codes follow Unix conventions for proper integration with shell scripts.

* * *

### 14. Testing with CliRunner

**Status**: Recommended

**Details**:

Use Typer’s CliRunner for testing commands:

```python
# tests/test_commands.py
import pytest
from typer.testing import CliRunner
from myproject.cli import app

runner = CliRunner()


def test_list_command() -> None:
    """Test list command returns expected output."""
    result = runner.invoke(app, ["list", "--limit", "5"])
    assert result.exit_code == 0
    assert "items" in result.stdout or "No items found" in result.stdout


def test_list_json_format() -> None:
    """Test JSON output format."""
    result = runner.invoke(app, ["list", "--format", "json"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.stdout)
    assert "items" in data
    assert "total" in data


def test_dry_run() -> None:
    """Test dry-run mode doesn't make changes."""
    result = runner.invoke(app, ["create", "--name", "test", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY-RUN" in result.stdout


def test_invalid_option() -> None:
    """Test invalid options return proper exit code."""
    result = runner.invoke(app, ["list", "--invalid-option"])
    assert result.exit_code == 2


@pytest.fixture
def isolated_filesystem(tmp_path):
    """Fixture for tests that need filesystem isolation."""
    import os
    original = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original)


def test_command_with_file(isolated_filesystem) -> None:
    """Test command that works with files."""
    # Create test file
    test_file = isolated_filesystem / "input.txt"
    test_file.write_text("test content")

    result = runner.invoke(app, ["process", str(test_file)])
    assert result.exit_code == 0
```

**Assessment**: CliRunner provides isolated testing without subprocess overhead.
Tests can verify exit codes, stdout/stderr output, and side effects.

* * *

### 15. Interactive Prompts with Questionary

**Status**: Situational

**Details**:

For interactive CLIs, use questionary for prompts (works well with Rich):

```python
# lib/prompts.py
import questionary
from rich.console import Console

console = Console()


def confirm(message: str, default: bool = False, auto_yes: bool = False) -> bool:
    """Confirm action with user, respecting --yes flag."""
    if auto_yes:
        return True
    return questionary.confirm(message, default=default).ask() or False


def select(message: str, choices: list[str]) -> str | None:
    """Select from a list of choices."""
    return questionary.select(message, choices=choices).ask()


def text_input(message: str, default: str = "") -> str:
    """Get text input from user."""
    return questionary.text(message, default=default).ask() or ""


# Usage with --yes flag for non-interactive mode:
@app.command()
def create(
    ctx: typer.Context,
    name: Annotated[str | None, typer.Option()] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmations")] = False,
) -> None:
    """Create a new resource."""
    if name is None:
        if yes:
            raise typer.BadParameter("--name required with --yes")
        name = text_input("Resource name:")

    if not confirm(f"Create resource '{name}'?", auto_yes=yes):
        raise typer.Abort()

    # Proceed with creation...
```

**Assessment**: Questionary provides beautiful prompts that integrate well with Rich.
Always support a `--yes` flag to enable non-interactive automation.

* * *

### 16. Documentation Command

**Status**: Recommended

**Details**:

Add a `docs` command that shows comprehensive help:

```python
# commands/docs.py
import typer
from rich.console import Console
from rich.markdown import Markdown
from importlib.resources import files

app = typer.Typer()
console = Console()


@app.command()
def show() -> None:
    """Show full documentation for all commands."""
    try:
        # Load README from package resources
        readme_path = files("myproject").joinpath("README.md")
        content = readme_path.read_text()
        md = Markdown(content)
        console.print(md)
    except Exception:
        # Fallback to help
        console.print("[dim]Documentation not available. Use --help for command info.[/dim]")


def get_all_commands_help(app: typer.Typer) -> str:
    """Generate help text for all commands."""
    from click import Context
    from io import StringIO

    output = StringIO()
    # Iterate through commands and collect help
    # ...
    return output.getvalue()
```

**Assessment**: A docs command provides a single reference for all CLI functionality,
especially valuable for CLIs with many subcommands.

* * *

## Best Practices Summary

1. **Support agent/automation modes** with `--non-interactive`, `--yes`, and
   `--no-progress` flags; also respect `CI` env var

2. **Disable spinners/progress in non-TTY** — agent context window flooding is a severe
   antipattern

3. **Use the modern tooling stack** (uv, Typer/argparse+rich_argparse, Rich, Ruff,
   BasedPyright)

4. **Use Base Command pattern** to eliminate boilerplate across commands

5. **Support dual output modes** (text, JSON, jsonl) through OutputManager

6. **Raise CLIError exceptions**, handle exits only at entrypoint

7. **Use standard exit codes**: 0 success, 1 error, 2 validation, 130 interrupted

8. **Route output correctly**: data to stdout, spinners/errors to stderr

9. **Separate handlers from command definitions** for testability

10. **Use TypedDict or dataclasses** for type-safe options

11. **Pair text and JSON formatters** for each data domain

12. **Use git-based versioning** via uv-dynamic-versioning

13. **Define global options at app level** using Typer’s callback

14. **Support `--color auto|always|never`** and respect `NO_COLOR` env var

15. **Support --dry-run** for safe testing of destructive commands

16. **Test with CliRunner** for isolated, fast tests

17. **Add docs/schema/examples commands** for human and machine documentation

* * *

## References

### Documentation

- [Typer](https://typer.tiangolo.com/) — Modern CLI framework (type-hint based)

- [rich_argparse](https://github.com/hamdanal/rich_argparse) — Rich formatting for
  argparse

- [Rich](https://rich.readthedocs.io/) — Terminal formatting and output

- [uv](https://docs.astral.sh/uv/) — Modern Python package manager

- [Ruff](https://docs.astral.sh/ruff/) — Fast linter and formatter

- [BasedPyright](https://docs.basedpyright.com/) — Type checker

- [questionary](https://questionary.readthedocs.io/) — Interactive prompts

### Related Documentation

- [Modern TypeScript CLI Patterns](research-modern-typescript-cli-patterns.md) —
  Equivalent patterns for TypeScript CLIs

- [Modern TypeScript Monorepo Package](research-modern-typescript-monorepo-package.md) —
  Build tooling, package exports, CI/CD

### Example Projects

- [simple-modern-uv](https://github.com/jlevy/simple-modern-uv) — Modern Python project
  template

- [uvtemplate](https://github.com/jlevy/uvtemplate) — Example CLI using Typer patterns

- [clideps](https://github.com/jlevy/clideps) — Example CLI using argparse +
  rich_argparse patterns (see
  [readable_argparse.py](https://github.com/jlevy/clideps/blob/main/src/clideps/utils/readable_argparse.py)
  for enhanced formatter)
