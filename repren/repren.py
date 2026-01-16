#!/usr/bin/env python
r"""
## Rename Anything

`repren` is a powerful CLI string replacement and file renaming tool for use by agents
or humans for almost any search-and-replace or renaming task.

It is small, self-contained, self-documenting, and works on Python 3.10-3.14 with zero
dependencies. Essentially, it is a general-purpose, brute-force text file refactoring
tool.

For example, repren could rename occurrences of certain names in a set of source files,
while simultaneously renaming the files and directories according to the same pattern
and handling all case variations.

It’s more powerful than classic options like `perl -pie`, `rpl`, or `sed`:

- **Replacements:** It allows rewriting file contents according to one or more literal
  or regular expression patterns.

- **Renames:** It can also apply the patterns to rename or move files according to
  replacements on their full paths, creating directories as needed.

- **Regexes:** It supports fully expressive regular expressions substitutions, including
  matching groups for back substitutions (like `\1`, `\2`, etc.).

- **Simultaneous renames:** It performs simultaneous renamings: you can make as many
  replacements as you want and you can rename “foo” as “bar”, and “bar” as “foo” at
  once, without requiring a temporary intermediate rename.

- **Good hygiene:** It is careful: it has a nondestructive “dry run” mode and prints
  clear stats on its changes.
  It leaves backups. File operations are done atomically, so interruptions never leave a
  previously existing file truncated or partly edited.

- **Case preserving options:** It supports “magic” case-preserving renames that let you
  find and rename identifiers with case variants (lowerCamel, UpperCamel,
  lower_underscore, and UPPER_UNDERSCORE) consistently.

- **Dry run, backups, and undo:** It has convenient options for dry run, undo (restoring
  backups), and cleanup (deleting backups).

- **Text or JSON output:** It supports human-readable text output (default) or
  machine-parseable JSON output (`--format=json`) for easy integration with scripts and
  agents.

- **Self-documenting:** It is packaged with its own nice documentation!
  Run `repren --docs` for full documentation.

If file paths are provided, repren replaces those files in place, leaving a backup with
extension “.orig” (controlled by the `--backup-suffix` option).

If directory paths are provided, it applies replacements recursively to all files in the
supplied paths that are not in the exclude pattern.
If no arguments are supplied, it reads from stdin and writes to stdout.

## Examples

Patterns can be supplied in a text file, with one or more replacements consisting of
regular expression and replacement.
For example:

```
# Sample pattern file
frobinator<tab>glurp
WhizzleStick<tab>AcmeExtrudedPlasticFunProvider
figure ([0-9+])<tab>Figure \1
```

(Where `<tab>` is an actual tab character.)
Each line is a replacement.
Empty lines and #-prefixed comments are ignored.

As a short-cut, a single replacement can be specified on the command line using `--from`
(match) and `--to` (replacement).

Examples:

```bash
# Here `patfile` is a patterns file.
# Rewrite stdin:
repren --patterns=patfile < input > output

# Shortcut with a single pattern replacement (replace foo with bar):
repren --from=foo --to=bar < input > output

# Rewrite a few files in place, also requiring matches be on word breaks:
repren --patterns=patfile --word-breaks myfile1 myfile2 myfile3

# Rewrite whole directory trees. Since this is a big operation, we use
# `-n` to do a dry run that only prints what would be done:
repren -n --patterns=patfile --word-breaks --full mydir1

# Now actually do it:
repren --patterns=patfile --word-breaks --full mydir1

# Same as above, for all case variants:
repren --patterns=patfile --word-breaks --preserve-case --full mydir1

# Same as above but including only .py files and excluding the tests directory
# and any files or directories starting with test_:
repren --patterns=patfile --word-breaks --preserve-case --full --include='.*[.]py$' --exclude='tests|test_.*' mydir1
```

## Usage

Run `repren --docs` for full usage and flags.

If file paths are provided, repren replaces those files in place, leaving a backup with
extension “.orig”. If directory paths are provided, it applies replacements recursively
to all files in the supplied paths that are not in the exclude pattern.
If no arguments are supplied, it reads from stdin and writes to stdout.

## Alternatives

There are many tools for search/replace and refactoring. Here's how repren compares:

### Comparison

| Feature | repren | [sed/awk/perl](http://stackoverflow.com/questions/11392478/how-to-replace-a-string-in-multiple-files-in-linux-command-line/29191549) | [sd](https://github.com/chmln/sd) | [fastmod](https://github.com/facebookincubator/fastmod) | [ast-grep](https://ast-grep.github.io/) | [comby](https://comby.dev/) | [rnr](https://github.com/ismaelgv/rnr) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Simultaneous edits and swaps (foo↔bar) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| File/directory renaming | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Case-preserving variants | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Language-agnostic | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Structural/AST-aware | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Interactivity | Dry run, backups, undo | ❌ | ❌ | Interactive review | Interactive review | Interactive review | Dry run, backups, undo |
| Dependencies | Python 3.10+ (no other deps) | Varies (OS/shell) | Binary (Rust) | Binary (Rust) | Binary (Rust) | Binary (OCaml) | Binary (Rust) |

**When to use each:**

- **repren**: Bulk renames with file/directory renaming, case preservation, or simultaneous
  swaps. Works on any text file with full backup/undo support.
- **sed/awk/perl**: Classic approaches for quick one-liners. See
  [classic approaches](http://stackoverflow.com/questions/11392478/how-to-replace-a-string-in-multiple-files-in-linux-command-line/29191549).
  Often error-prone for complex patterns and lack dry-run mode, simultaneous swaps, or
  cross-platform consistency.
- **sd**: Fast sed replacement (2-11x faster than sed), but limited to simple find/replace
  without file renaming, case preservation, or multi-pattern swaps.
- **fastmod**: Good for interactive human review of changes, but lacks case preservation,
  simultaneous swaps, and file/directory renaming.
- **ast-grep**: Language-aware refactoring where you need to match code structure (e.g.,
  function calls, not just text). Use when semantic understanding matters more than speed.
- **comby**: Structural matching across languages without learning AST syntax. Useful when
  you need to match code patterns like balanced braces, but overkill for simple text
  refactoring.
- **rnr**: File/directory renaming only (no content replacement). Has dry-run by default,
  backup option, and undo via dump files. Use repren if you also need content replacement.

## Installation

No dependencies except Python 3.10+. It’s easiest to install with
[uv](https://docs.astral.sh/uv/):

```bash
# Install as a tool:
uv tool install repren

# Or run directly without installing:
uvx repren --help
```

Or, since it’s just one file, you can copy the
[repren.py](https://raw.githubusercontent.com/jlevy/repren/master/repren/repren.py)
script somewhere convenient and make it executable.

## Agent Use

### Why Agents Should Use repren

repren is designed for use by AI coding agents (Claude Code, Codex, etc.)
as well as humans.

AST-based tools (ast-grep, Semgrep, ts-morph) can be better for focused, language-aware
semantic refactoring.
But repren is ideal for fast, large code or doc text refactoring, file/directory
renaming, or any serious larger-scale renaming effort:

| Feature | repren | AST tools | Built-in Edit |
| --- | --- | --- | --- |
| Simultaneous renames and swaps (foo↔bar) | ✅ | ❌ | ❌ |
| File/directory renaming | ✅ | Some | ❌ |
| Case-preserving variants | ✅ | ❌ | ❌ |
| Works on any text file | ✅ | ❌ | ✅ |
| Dry runs, backups, undo system | ✅ | ❌ | ❌ |

### JSON Output

Use `--format=json` for machine-parseable output:

```bash
repren --format=json --from=foo --to=bar --full src/
```

### Claude Code Skill

repren includes a built-in skill for [Claude Code](https://claude.com/claude-code), so
Claude can use repren for bulk refactoring tasks.

**Install:**

```bash
# Install globally (available in all projects):
uvx repren --install-skill

# Or install for current project only (shareable via git):
uvx repren --install-skill --agent-base=./.claude
```

Re-run to update an existing installation.

**Manual install:** Run `uvx repren --skill` and save to
`~/.claude/skills/repren/SKILL.md` (global) or `.claude/skills/repren/SKILL.md`
(project).

**Learn more:** [Claude Code docs](https://claude.ai/code) and
[Skills repository](https://github.com/anthropics/skills).

## Try It

Let’s try a simple replacement in my working directory (which has a few random source
files):

```bash
$ repren --from=frobinator-server --to=glurp-server --full --dry-run .
Dry run: No files will be changed
Using 1 patterns:
  'frobinator-server' -> 'glurp-server'
Found 102 files in: .
- modify: ./site.yml: 1 matches
- rename: ./roles/frobinator-server/defaults/main.yml -> ./roles/glurp-server/defaults/main.yml
- rename: ./roles/frobinator-server/files/deploy-frobinator-server.sh -> ./roles/glurp-server/files/deploy-frobinator-server.sh
- rename: ./roles/frobinator-server/files/install-graphviz.sh -> ./roles/glurp-server/files/install-graphviz.sh
- rename: ./roles/frobinator-server/files/frobinator-purge-old-deployments -> ./roles/glurp-server/files/frobinator-purge-old-deployments
- rename: ./roles/frobinator-server/handlers/main.yml -> ./roles/glurp-server/handlers/main.yml
- rename: ./roles/frobinator-server/tasks/main.yml -> ./roles/glurp-server/tasks/main.yml
- rename: ./roles/frobinator-server/templates/frobinator-webservice.conf.j2 -> ./roles/glurp-server/templates/frobinator-webservice.conf.j2
- rename: ./roles/frobinator-server/templates/frobinator-webui.conf.j2 -> ./roles/glurp-server/templates/frobinator-webui.conf.j2
Read 102 files (190382 chars), found 2 matches (0 skipped due to overlaps)
Dry run: Would have changed 2 files, including 0 renames
```

That was a dry run, so if it looks good, it’s easy to repeat that a second time,
dropping the `--dry-run` flag.
If this is in git, we’d do a git diff to verify, test, then commit it all.
If we messed up, there are still .orig files present.

## Patterns

Patterns can be supplied using the `--from` and `--to` syntax above, but that only works
for a single pattern.

In general, you can perform multiple simultaneous replacements by putting them in a
*patterns file*. Each line consists of a regular expression and replacement.
For example:

```
# Sample pattern file
frobinator<tab>glurp
WhizzleStick<tab>AcmeExtrudedPlasticFunProvider
figure ([0-9+])<tab>Figure \1
```

(Where `<tab>` is an actual tab character.)

Empty lines and #-prefixed comments are ignored.
Capturing groups and back substitutions (such as \1 above) are supported.

## Examples

```
# Here `patfile` is a patterns file.
# Rewrite stdin:
repren --patterns=patfile < input > output

# Shortcut with a single pattern replacement (replace foo with bar):
repren --from=foo --to=bar < input > output

# Rewrite a few files in place, also requiring matches be on word breaks:
repren --patterns=patfile --word-breaks myfile1 myfile2 myfile3

# Rewrite whole directory trees. Since this is a big operation, we use
# `-n` to do a dry run that only prints what would be done:
repren -n --patterns=patfile --word-breaks --full mydir1

# Now actually do it:
repren --patterns=patfile --word-breaks --full mydir1

# Same as above, for all case variants:
repren --patterns=patfile --word-breaks --preserve-case --full mydir1
```

## Backup Management

Repren provides tools for managing backup files created during operations:

### Undo Changes

If you need to revert changes, use `--undo` with the same patterns as the original
operation:

```bash
# Original operation:
repren --from=OldClass --to=NewClass --full src/

# Undo the changes:
repren --undo --from=OldClass --to=NewClass --full src/
```

The undo command:
- Finds all `.orig` backup files
- Uses the patterns to determine which files were renamed
- Restores the original files and removes renamed files
- Skips with warnings if timestamps look wrong or files are missing

### Clean Backups

When you’re satisfied with your changes, remove backup files:

```bash
# Remove all .orig backup files:
repren --clean-backups src/

# Dry run to see what would be removed:
repren --clean-backups --dry-run src/

# Remove backups with custom suffix:
repren --clean-backups --backup-suffix=.bak src/
```

### Complete Workflow

A typical workflow:

```bash
# 1. Preview changes
repren --dry-run --from=foo --to=bar --full mydir/

# 2. Execute changes (creates .orig backups)
repren --from=foo --to=bar --full mydir/

# 3. Review and test your changes

# 4. Either undo if something went wrong:
repren --undo --from=foo --to=bar --full mydir/

# 4. Or clean up backups when satisfied:
repren --clean-backups mydir/
```

## Notes

- All pattern matching is via standard
  [Python regular expressions](https://docs.python.org/3/library/re.html).

- As with sed, replacements are made line by line by default.
  Memory permitting, replacements may be done on entire files using `--at-once`.

- As with sed, replacement text may include backreferences to groups within the regular
  expression, using the usual syntax: \1, \2, etc.

- In the pattern file, both the regular expression and the replacement may contain the
  usual escapes `\\n`, `\\t`, etc.
  (To match a multi-line pattern, containing `\\n`, you must use `--at-once`.)

- Replacements are all matched on each input file, then all replaced, so it’s possible
  to swap or otherwise change names in ways that would require multiple steps if done
  one replacement at a time.

- If two patterns have matches that overlap, only one replacement is applied, with
  preference to the pattern appearing first in the patterns file.

- If one pattern is a subset of another, consider if `--word-breaks` will help.

- If patterns have special characters, `--literal` may help.

- The case-preserving option works by adding all case variants to the pattern
  replacements, e.g. if the pattern file has foo_bar -> xxx_yyy, the replacements fooBar
  -> xxxYyy, FooBar -> XxxYyy, FOO_BAR -> XXX_YYY are also made.
  Assumes each pattern has one casing convention.

- The same logic applies to filenames, with patterns applied to the full file path with
  slashes replaced and then parent directories created as needed, e.g.
  `my/path/to/filename` can be rewritten to `my/other/path/to/otherfile`. (Use caution
  and test with `-n`, especially when using absolute path arguments!)

- Files are never clobbered by renames.
  If a target already exists, or multiple files are renamed to the same target, numeric
  suffixes will be added to make the files distinct (".1", “.2”, etc.).

- Files are created at a temporary location, then renamed, so original files are left
  intact in case of unexpected errors.
  File permissions are preserved.

- Backups are created of all modified files, with the suffix “.orig”.
  The suffix can be customized with `--backup-suffix`.

- By default, recursive searching omits paths starting with “.”. This may be adjusted
  with `--exclude`. Files ending in the backup suffix (`.orig` by default) are always
  ignored.

- Data is handled as bytes internally, allowing it to work with any encoding or binary
  files. File contents are not decoded unless necessary (e.g., for logging).
  However, patterns are specified as strings in the pattern file and command line
  arguments, and file paths are handled as strings for filesystem operations.
"""

from __future__ import annotations

import argparse
import bisect
import importlib.metadata
import json
import os
import re
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass
from re import Match, Pattern
from typing import Any, BinaryIO, Literal, NoReturn

# override decorator is only available in Python 3.12+
if sys.version_info >= (3, 12):
    from typing import override
else:
    # For Python 3.10 and 3.11, create a no-op decorator
    from typing import TypeVar

    _F = TypeVar("_F", bound=Callable[..., Any])

    def override(method: _F, /) -> _F:
        return method


# Type aliases for clarity.
OutputFormat = Literal["text", "json"]
PatternType = tuple[Pattern[bytes], bytes]
FileHandle = BinaryIO
MatchType = Match[bytes]
PatternPair = tuple[MatchType, bytes]
TransformFunc = Callable[[bytes], tuple[bytes, "_MatchCounts"]]
LogFunc = Callable[[str], None]
FailHandler = Callable[[str, Exception | None], None]


# --- Exit codes (following Unix conventions) ---


EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_INTERRUPTED = 130  # 128 + SIGINT(2)


# --- Custom exceptions ---


class CLIError(Exception):
    """Base exception for CLI errors."""

    message: str
    exit_code: int

    def __init__(self, message: str, exit_code: int = EXIT_ERROR) -> None:
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class ValidationError(CLIError):
    """Input validation or usage error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=EXIT_USAGE)


# Get the version from package metadata.
def _get_version() -> str:
    try:
        return importlib.metadata.version("repren")
    except importlib.metadata.PackageNotFoundError:
        # Fallback version if package metadata is not available.
        return "0.0.0.dev"


VERSION: str = _get_version()

DESCRIPTION: str = "Powerful CLI string replacement and file renaming for agents and humans"

BACKUP_SUFFIX: str = ".orig"
TEMP_SUFFIX: str = ".repren.tmp"
DEFAULT_EXCLUDE_PAT: str = r"^\."

# Hint message for help and error output.
DOCS_HINT: str = """\
Run `repren --help` for usage.
Run `repren --docs` for full docs."""

# Terminal width handling.
DEFAULT_WIDTH: int = 88
MIN_WIDTH: int = 40
MAX_WIDTH: int = 88


def _is_ci() -> bool:
    """Check if running in a CI environment."""
    return bool(os.environ.get("CI"))


def _get_terminal_width() -> int:
    """Get terminal width, clamped to reasonable bounds.

    Uses DEFAULT_WIDTH when not connected to a TTY or in CI environments
    for consistent output in scripts and automated pipelines.
    """
    if not sys.stdout.isatty() or _is_ci():
        return DEFAULT_WIDTH
    try:
        width = shutil.get_terminal_size().columns
        return min(MAX_WIDTH, max(MIN_WIDTH, width))
    except Exception:
        return DEFAULT_WIDTH


def no_log(_msg: str) -> None:
    pass


def print_stderr(msg: str) -> None:
    print(msg, file=sys.stderr)


def _fail_with_exit(msg: str, e: Exception | None = None) -> NoReturn:
    """Fail by exiting the process (used when running as CLI)."""
    if e:
        msg = f"{msg}: {e}" if msg else str(e)
    print("error: " + msg, file=sys.stderr)
    sys.exit(EXIT_ERROR)


def _fail_with_exception(msg: str, e: Exception | None = None) -> NoReturn:
    """Fail by raising an exception (used when used as a library)."""
    raise CLIError(msg) from e


# By default, fail with exceptions in case we want to use this as a library.
_fail: FailHandler = _fail_with_exception


def safe_decode(b: bytes) -> str:
    """
    Safely decode bytes to a string for logging purposes.
    Replaces invalid UTF-8 sequences to prevent errors.
    """
    return b.decode("utf-8", errors="backslashreplace")


# --- Markdown rendering (optional, imported dynamically) ---
# Try to import markdown_renderer from the repren package for enhanced rendering.
# If not available (e.g., standalone script), markdown is readable as-is.

_markdown_available = False
_ansi_yellow = ""
_ansi_reset = ""

try:
    from .markdown_renderer import ANSI
    from .markdown_renderer import render_markdown as _render_markdown

    _markdown_available = True
    _ansi_yellow = ANSI.YELLOW
    _ansi_reset = ANSI.RESET
except ImportError:
    # Fallback: clean markdown is already readable, just return as-is
    def _render_markdown(text: str, color: bool = True) -> str:
        """Fallback: return markdown text unchanged (already readable)."""
        del color  # Unused in fallback, but required for signature compatibility
        return text


def _format_hint(color: bool = True) -> str:
    """Format the DOCS_HINT with optional ANSI colors."""
    if color and _markdown_available:
        return f"{_ansi_yellow}{DOCS_HINT}{_ansi_reset}"
    return DOCS_HINT


@dataclass
class _Tally:
    files: int = 0
    chars: int = 0
    matches: int = 0
    valid_matches: int = 0
    files_changed: int = 0
    files_rewritten: int = 0
    renames: int = 0


_tally: _Tally = _Tally()


def _output_json(result: dict[str, Any]) -> None:
    """Output a JSON result to stdout."""
    print(json.dumps(result, indent=2))


# --- String matching ---


def _overlap(match1: MatchType, match2: MatchType) -> bool:
    return match1.start() < match2.end() and match2.start() < match1.end()


def _sort_drop_overlaps(
    matches: list[PatternPair],
    source_name: str | None = None,
    log: LogFunc = no_log,
) -> list[PatternPair]:
    """Select and sort a set of disjoint intervals, omitting ones that overlap."""
    non_overlaps: list[PatternPair] = []
    starts: list[int] = []
    for match, replacement in matches:
        index: int = bisect.bisect_left(starts, match.start())
        if index > 0:
            (prev_match, _) = non_overlaps[index - 1]
            if _overlap(prev_match, match):
                log(
                    f"- {source_name}: Skipping overlapping match '{safe_decode(match.group())}' "
                    f"of '{safe_decode(match.re.pattern)}' that overlaps "
                    f"'{safe_decode(prev_match.group())}' of '{safe_decode(prev_match.re.pattern)}' on its left"
                )
                continue
        if index < len(non_overlaps):
            (next_match, _) = non_overlaps[index]
            if _overlap(next_match, match):
                log(
                    f"- {source_name}: Skipping overlapping match '{safe_decode(match.group())}' "
                    f"of '{safe_decode(match.re.pattern)}' that overlaps "
                    f"'{safe_decode(next_match.group())}' of '{safe_decode(next_match.re.pattern)}' on its right"
                )
                continue
        starts.insert(index, match.start())
        non_overlaps.insert(index, (match, replacement))
    return non_overlaps


def _apply_replacements(input_bytes: bytes, matches: list[PatternPair]) -> bytes:
    out: list[bytes] = []
    pos: int = 0
    for match, replacement in matches:
        out.append(input_bytes[pos : match.start()])
        out.append(match.expand(replacement))
        pos = match.end()
    out.append(input_bytes[pos:])
    return b"".join(out)


@dataclass
class _MatchCounts:
    found: int = 0
    valid: int = 0

    def add(self, o: _MatchCounts) -> None:
        self.found += o.found
        self.valid += o.valid


def multi_replace(
    input_bytes: bytes,
    patterns: list[PatternType],
    is_path: bool = False,
    source_name: str | None = None,
    log: LogFunc = no_log,
) -> tuple[bytes, _MatchCounts]:
    """
    Replace all occurrences in the input given a list of patterns (regex,
    replacement), simultaneously, so that no replacement affects any other.
    """
    matches: list[PatternPair] = []
    for regex, replacement in patterns:
        for match in regex.finditer(input_bytes):
            matches.append((match, replacement))
    valid_matches: list[PatternPair] = _sort_drop_overlaps(
        matches, source_name=source_name, log=log
    )
    result: bytes = _apply_replacements(input_bytes, valid_matches)

    global _tally
    if not is_path:
        _tally.chars += len(input_bytes)
        _tally.matches += len(matches)
        _tally.valid_matches += len(valid_matches)

    return result, _MatchCounts(len(matches), len(valid_matches))


# --- Case handling (only used for case-preserving magic) ---


_name_pat = re.compile(r"\w+")


def _split_name(name: str) -> tuple[str, list[str]]:
    """
    Split a CamelCase or underscore-formatted name into words.
    Return separator and list of words.
    """
    # TODO: Could handle dash-separated names as well.
    if "_" in name:
        # Underscore-separated name
        return "_", name.split("_")
    else:
        # CamelCase or mixed case name
        words = []
        current_word = ""
        i = 0
        while i < len(name):
            char = name[i]
            if i > 0 and char.isupper():
                if name[i - 1].islower() or (i + 1 < len(name) and name[i + 1].islower()):
                    # Start a new word
                    words.append(current_word)
                    current_word = char
                else:
                    current_word += char
            else:
                current_word += char
            i += 1
        if current_word:
            words.append(current_word)
        return "", words


def _capitalize(word: str) -> str:
    return word[0].upper() + word[1:].lower() if word else ""  # Handle empty strings safely


def to_lower_camel(name: str) -> str:
    _, words = _split_name(name)
    return words[0].lower() + "".join(_capitalize(word) for word in words[1:])


def to_upper_camel(name: str) -> str:
    _, words = _split_name(name)
    return "".join(_capitalize(word) for word in words)


def to_lower_underscore(name: str) -> str:
    _, words = _split_name(name)
    return "_".join(word.lower() for word in words)


def to_upper_underscore(name: str) -> str:
    _, words = _split_name(name)
    return "_".join(word.upper() for word in words)


def _transform_expr(expr: str, transform: Callable[[str], str]) -> str:
    transformed = _name_pat.sub(lambda m: transform(m.group()), expr)
    return transformed


def all_case_variants(expr: str) -> list[str]:
    """
    Return all casing variations of an expression.
    Note: This operates on strings and is called before pattern compilation.
    """
    return [
        _transform_expr(expr, transform)
        for transform in [to_lower_camel, to_upper_camel, to_lower_underscore, to_upper_underscore]
    ]


# --- File handling ---


def make_parent_dirs(path: str) -> str:
    """
    Ensure parent directories of a file are created as needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def move_file(source_path: str, dest_path: str, clobber: bool = False) -> None:
    """
    Move a file, adding a numeric suffix if the destination already exists.
    """
    if not clobber:
        trailing_num = re.compile(r"(.*)[.]\d+$")
        i = 1
        while os.path.exists(dest_path):
            match = trailing_num.match(dest_path)
            if match:
                dest_path = match.group(1)
            dest_path = f"{dest_path}.{i}"
            i += 1
    shutil.move(source_path, dest_path)


def transform_stream(
    transform: TransformFunc | None,
    stream_in: BinaryIO,
    stream_out: BinaryIO,
    by_line: bool = False,
) -> _MatchCounts:
    """
    Transform a stream of bytes, either line-by-line or at once in memory.
    """
    counts = _MatchCounts()
    if by_line:
        for line in stream_in:  # line will be bytes
            if transform:
                (new_line, new_counts) = transform(line)
                counts.add(new_counts)
            else:
                new_line = line
            stream_out.write(new_line)
    else:
        contents = stream_in.read()  # contents will be bytes
        (new_contents, new_counts) = (
            transform(contents) if transform else (contents, _MatchCounts())
        )
        counts.add(new_counts)
        stream_out.write(new_contents)
    return counts


def transform_file(
    transform: TransformFunc | None,
    source_path: str,
    dest_path: str,
    orig_suffix: str = BACKUP_SUFFIX,
    temp_suffix: str = TEMP_SUFFIX,
    by_line: bool = False,
    dry_run: bool = False,
) -> _MatchCounts:
    """
    Transform full contents of file at source_path with specified function,
    either line-by-line or at once in memory, writing dest_path atomically and
    keeping a backup. Source and destination may be the same path.
    """
    counts = _MatchCounts()
    global _tally
    changed = False
    if transform:
        orig_path = source_path + orig_suffix
        temp_path = dest_path + temp_suffix
        # TODO: This will create a directory even in dry_run mode, but perhaps that's acceptable.
        # https://github.com/jlevy/repren/issues/6
        make_parent_dirs(temp_path)
        perms = os.stat(source_path).st_mode & 0o777
        with open(source_path, "rb") as stream_in:
            with os.fdopen(os.open(temp_path, os.O_WRONLY | os.O_CREAT, perms), "wb") as stream_out:
                counts = transform_stream(transform, stream_in, stream_out, by_line=by_line)

        # All the above happens in dry-run mode so we get tallies.
        # Important: We don't modify original file until the above succeeds without exceptions.
        if not dry_run and (dest_path != source_path or counts.found > 0):
            move_file(source_path, orig_path, clobber=True)
            move_file(temp_path, dest_path, clobber=False)
        else:
            # If we're in dry-run mode, or if there were no changes at all, just forget the output.
            os.remove(temp_path)

        _tally.files += 1
        if counts.found > 0:
            _tally.files_rewritten += 1
            changed = True
        if dest_path != source_path:
            _tally.renames += 1
            changed = True
    elif dest_path != source_path:
        if not dry_run:
            make_parent_dirs(dest_path)
            move_file(source_path, dest_path, clobber=False)
        _tally.files += 1
        _tally.renames += 1
        changed = True
    if changed:
        _tally.files_changed += 1

    return counts


def rewrite_file(
    path: str,
    patterns: list[PatternType],
    do_renames: bool = False,
    do_contents: bool = False,
    backup_suffix: str = BACKUP_SUFFIX,
    by_line: bool = False,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> None:
    """
    Rewrite and/or rename the given file, making simultaneous changes according to the
    given list of patterns.
    """
    # Convert path to bytes for pattern matching, then back to str for filesystem ops.
    path_bytes = path.encode("utf-8")
    dest_path_bytes = (
        multi_replace(path_bytes, patterns, is_path=True, log=log)[0] if do_renames else path_bytes
    )
    dest_path = dest_path_bytes.decode("utf-8")

    transform = None
    if do_contents:
        transform = lambda contents: multi_replace(contents, patterns, source_name=path, log=log)
    counts = transform_file(
        transform, path, dest_path, orig_suffix=backup_suffix, by_line=by_line, dry_run=dry_run
    )
    if counts.found > 0:
        log(f"- modify: {path}: {counts.found} matches")
    if dest_path != path:
        log(f"- rename: {path} -> {dest_path}")


def walk_files(
    paths: list[str],
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    backup_suffix: str = BACKUP_SUFFIX,
) -> tuple[list[str], int]:
    """
    Walk the given paths and return files matching include/exclude patterns.
    Filters out backup files (ending with backup_suffix) and temp files.

    Returns a tuple of (list of file paths, count of skipped backup files).
    """
    include_re = re.compile(include_pat)
    exclude_re = re.compile(exclude_pat)
    out: list[str] = []
    skipped_backup_count = 0

    for path in paths:
        if os.path.isfile(path):
            f = os.path.basename(path)
            # Also filter explicit file paths that are backup files
            if path.endswith(backup_suffix) or path.endswith(TEMP_SUFFIX):
                skipped_backup_count += 1
            elif include_re.match(f) and not exclude_re.match(f):
                out.append(path)
        else:
            for root, dirs, files in os.walk(path):
                # Filter directories based on include and exclude patterns
                dirs[:] = [d for d in dirs if not exclude_re.match(d)]
                for f in files:
                    if f.endswith(backup_suffix) or f.endswith(TEMP_SUFFIX):
                        skipped_backup_count += 1
                    elif include_re.match(f) and not exclude_re.match(f):
                        out.append(os.path.join(root, f))

    out.sort()  # Ensure deterministic order of file processing.
    return out, skipped_backup_count


def rewrite_files(
    root_paths: list[str],
    patterns: list[PatternType],
    do_renames: bool = False,
    do_contents: bool = False,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    backup_suffix: str = BACKUP_SUFFIX,
    by_line: bool = False,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> None:
    """
    Walk the given `root_paths`, rewriting and/or renaming files making simultaneous
    changes according to the given list of patterns. Set `log` if you wish to log info
    in `dry_run` mode.
    """
    paths, skipped_backup_count = walk_files(
        root_paths,
        include_pat=include_pat,
        exclude_pat=exclude_pat,
        backup_suffix=backup_suffix,
    )
    if skipped_backup_count > 0:
        log(
            f"Skipped {skipped_backup_count} file(s) ending in '{backup_suffix}' "
            "(backup files are never processed)"
        )
    log(f"Found {len(paths)} files in: {', '.join(root_paths)}")
    for path in paths:
        rewrite_file(
            path,
            patterns,
            do_renames=do_renames,
            do_contents=do_contents,
            backup_suffix=backup_suffix,
            by_line=by_line,
            dry_run=dry_run,
            log=log,
        )


# --- Backup management ---


def find_backup_files(
    root_paths: list[str],
    backup_suffix: str = BACKUP_SUFFIX,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
) -> list[str]:
    """
    Find all files ending with the backup suffix in the given paths.
    """
    include_re = re.compile(include_pat)
    exclude_re = re.compile(exclude_pat)
    out: list[str] = []

    for path in root_paths:
        if os.path.isfile(path):
            f = os.path.basename(path)
            if path.endswith(backup_suffix) and include_re.match(f) and not exclude_re.match(f):
                out.append(path)
        else:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not exclude_re.match(d)]
                for f in files:
                    if (
                        f.endswith(backup_suffix)
                        and include_re.match(f)
                        and not exclude_re.match(f)
                    ):
                        out.append(os.path.join(root, f))

    out.sort()
    return out


def undo_backups(
    root_paths: list[str],
    patterns: list[PatternType],
    backup_suffix: str = BACKUP_SUFFIX,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> tuple[int, int]:
    """
    Restore original files from backups using patterns to reverse renames.

    For each backup file (e.g., foo.txt.orig):
    1. Strip suffix to get original path (foo.txt)
    2. Apply patterns to predict what the file was renamed to
    3. Validate predicted file exists and timestamps are correct
    4. Restore original and remove renamed file (if applicable)

    Skips with warnings (no action taken) when:
    - Predicted renamed file doesn't exist
    - Backup is newer than current file (unexpected timestamp order)

    Returns (restored_count, skipped_count).
    """
    backup_files = find_backup_files(
        root_paths,
        backup_suffix=backup_suffix,
        include_pat=include_pat,
        exclude_pat=exclude_pat,
    )

    restored = 0
    skipped = 0

    for backup_path in backup_files:
        # Strip the backup suffix to get the original path
        original_path = backup_path[: -len(backup_suffix)]

        # Apply patterns to predict the renamed path
        original_path_bytes = original_path.encode("utf-8")
        predicted_path_bytes, _ = multi_replace(original_path_bytes, patterns, is_path=True)
        predicted_path = predicted_path_bytes.decode("utf-8")

        # Determine which file should exist (original or renamed)
        if predicted_path == original_path:
            # No rename happened, just content change
            target_path = original_path
        else:
            # File was renamed
            target_path = predicted_path

        # Check if target file exists
        if not os.path.exists(target_path):
            log(f"- skip: {backup_path}: expected '{target_path}' not found")
            skipped += 1
            continue

        # Check timestamps: backup should be older than current file
        backup_mtime = os.path.getmtime(backup_path)
        target_mtime = os.path.getmtime(target_path)
        if backup_mtime > target_mtime:
            log(f"- skip: {backup_path}: backup is newer than current file")
            skipped += 1
            continue

        # Perform the undo
        if not dry_run:
            # Move backup to original location
            shutil.move(backup_path, original_path)
            # Remove the renamed file if it's different from original
            if predicted_path != original_path and os.path.exists(predicted_path):
                os.remove(predicted_path)
            log(f"- restore: {backup_path} -> {original_path}")
        else:
            log(f"- restore (dry-run): {backup_path} -> {original_path}")

        restored += 1

    return restored, skipped


def clean_backups(
    root_paths: list[str],
    backup_suffix: str = BACKUP_SUFFIX,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> int:
    """
    Remove backup files.

    Returns the count of files removed (or that would be removed in dry_run mode).
    """
    backup_files = find_backup_files(
        root_paths,
        backup_suffix=backup_suffix,
        include_pat=include_pat,
        exclude_pat=exclude_pat,
    )

    removed = 0
    for backup_path in backup_files:
        if not dry_run:
            os.remove(backup_path)
            log(f"- remove: {backup_path}")
        else:
            log(f"- remove (dry-run): {backup_path}")
        removed += 1

    return removed


# --- Invocation ---


def parse_patterns(
    patterns_str: str,
    literal: bool = False,
    word_breaks: bool = False,
    insensitive: bool = False,
    dotall: bool = False,
    preserve_case: bool = False,
) -> list[PatternType]:
    patterns: list[PatternType] = []
    flags = (re.IGNORECASE if insensitive else 0) | (re.DOTALL if dotall else 0)
    for line in patterns_str.splitlines():
        bits = None
        try:
            bits = line.split("\t")
            if line.strip().startswith("#"):
                continue
            elif line.strip() and len(bits) == 2:
                (regex, replacement) = bits
                if literal:
                    regex = re.escape(regex)
                pairs: list[tuple[str, str]] = []
                if preserve_case:
                    pairs += zip(
                        all_case_variants(regex), all_case_variants(replacement), strict=True
                    )
                pairs.append((regex, replacement))
                # Avoid spurious overlap warnings by removing dups.
                pairs = sorted(set(pairs))
                for regex_variant, replacement_variant in pairs:
                    if word_breaks:
                        regex_variant = r"\b" + regex_variant + r"\b"
                    # Convert to bytes here
                    patterns.append(
                        (
                            re.compile(regex_variant.encode("utf-8"), flags),
                            replacement_variant.encode("utf-8"),
                        )
                    )
        except Exception as e:
            _fail(f"error parsing pattern: {e}: {bits}", e)
    return patterns


def _run_cli() -> None:
    """Main CLI logic, separated for cleaner error handling."""
    width = _get_terminal_width()

    # Custom ArgumentParser that includes hint in error messages
    class HintArgumentParser(argparse.ArgumentParser):
        @override
        def error(self, message: str) -> NoReturn:
            self.print_usage(sys.stderr)
            hint = _format_hint(color=sys.stderr.isatty())
            self.exit(EXIT_USAGE, f"{self.prog}: error: {message}\n\n{hint}\n")

    parser = HintArgumentParser(
        description=DESCRIPTION,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog=prog, width=width),
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="show usage",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="show program's version number and exit",
    )
    parser.add_argument(
        "--docs",
        help="show full documentation",
        action="store_true",
    )
    parser.add_argument("--from", help="single replacement: match string", dest="from_pat")
    parser.add_argument("--to", help="single replacement: replacement string", dest="to_pat")
    parser.add_argument(
        "-p",
        "--patterns",
        help="file with multiple replacement patterns (see below)",
        dest="pat_file",
    )
    parser.add_argument(
        "--full",
        help="do file renames and search/replace on file contents",
        dest="do_full",
        action="store_true",
    )
    parser.add_argument(
        "--renames",
        help="do file renames only; do not modify file contents",
        dest="do_renames",
        action="store_true",
    )
    parser.add_argument(
        "--literal",
        help="use exact string matching, rather than regular expression matching",
        dest="literal",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--insensitive",
        help="match case-insensitively",
        dest="insensitive",
        action="store_true",
    )
    parser.add_argument("--dotall", help="match . to newlines", dest="dotall", action="store_true")
    parser.add_argument(
        "--preserve-case",
        help="do case-preserving magic to transform all case variants (see below)",
        dest="preserve_case",
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--word-breaks",
        help="require word breaks (regex \\b) around all matches",
        dest="word_breaks",
        action="store_true",
    )
    parser.add_argument(
        "--include",
        help="file name regex to include (default is .* to include all files)",
        dest="include_pat",
        default=".*",
    )
    parser.add_argument(
        "--exclude",
        help="file or directory name regex to exclude (default: paths starting with '.')",
        dest="exclude_pat",
        default=DEFAULT_EXCLUDE_PAT,
    )
    parser.add_argument(
        "--at-once",
        help="transform each file's contents at once, instead of line by line",
        dest="at_once",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--parse-only",
        help="parse and show patterns only",
        dest="parse_only",
        action="store_true",
    )
    parser.add_argument(
        "--walk-only",
        help=(
            "like --dry-run, but only walk directories and list files that will be processed "
            "(good for confirming your --include and --exclude patterns)"
        ),
        dest="walk_only",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        help="dry run: just log matches without changing files",
        dest="dry_run",
        action="store_true",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="quiet mode: suppress all output except errors",
        dest="quiet",
        action="store_true",
    )
    parser.add_argument(
        "--format",
        help="output format: 'text' for human-readable (default), 'json' for machine-parseable",
        dest="output_format",
        choices=["text", "json"],
        default="text",
    )
    parser.add_argument(
        "--backup-suffix",
        help=f"suffix for backup files (default: {BACKUP_SUFFIX})",
        dest="backup_suffix",
        default=BACKUP_SUFFIX,
    )
    parser.add_argument(
        "--undo",
        help="restore original files from backups (requires same patterns as original operation)",
        dest="undo",
        action="store_true",
    )
    parser.add_argument(
        "--clean-backups",
        help="remove backup files (standalone mode, no patterns needed)",
        dest="clean_backups",
        action="store_true",
    )
    parser.add_argument(
        "--install-skill",
        help="install Claude Code skill for repren (by default globally to ~/.claude/skills/repren)",
        dest="install_claude_skill",
        action="store_true",
    )
    parser.add_argument(
        "--agent-base",
        help="agent config directory for skills (e.g., './.claude' for project, defaults to ~/.claude)",
        dest="agent_base",
        metavar="DIR",
    )
    parser.add_argument(
        "--skill",
        help="print coding agent skill instructions (SKILL.md content)",
        dest="skill_instructions",
        action="store_true",
    )
    parser.add_argument("root_paths", nargs="*", help="root paths to process")

    # Handle --help early (show basic usage)
    if "-h" in sys.argv or "--help" in sys.argv:
        parser.print_help()
        print(f"\n{_format_hint(color=sys.stdout.isatty())}\n")
        sys.exit(0)

    # Handle --docs early (show full documentation)
    if "--docs" in sys.argv:
        doc_text = __doc__ or ""
        use_color = sys.stdout.isatty()
        full_docs = _render_markdown(doc_text, color=use_color) if _markdown_available else doc_text
        parser.epilog = full_docs + f"\n{_format_hint(color=use_color)}\n"
        parser.print_help()
        sys.exit(0)

    options = parser.parse_args()

    # Handle Claude skill installation (early exit)
    if options.install_claude_skill:
        try:
            from .claude_skill import install_skill

            # Install to specified agent base or ~/.claude by default
            install_skill(agent_base=options.agent_base)
            sys.exit(0)
        except ImportError:
            # Fallback if running as standalone script
            print(
                "Error: Claude skill installation requires full package installation.",
                file=sys.stderr,
            )
            print("Install with: uv tool install repren", file=sys.stderr)
            print("", file=sys.stderr)
            print(
                "Alternative: Download SKILL.md from the repository and install manually:",
                file=sys.stderr,
            )
            print("  mkdir -p ~/.claude/skills/repren", file=sys.stderr)
            print(
                "  curl -o ~/.claude/skills/repren/SKILL.md https://raw.githubusercontent.com/jlevy/repren/master/repren/skills/SKILL.md",
                file=sys.stderr,
            )
            sys.exit(1)

    # Handle skill instructions output (early exit)
    if options.skill_instructions:
        try:
            from .claude_skill import get_skill_content

            print(get_skill_content())
            print(f"\n{_format_hint(color=sys.stdout.isatty())}\n")
            sys.exit(0)
        except ImportError:
            # Fallback if running as standalone script
            print("Error: Skill instructions require full package installation.", file=sys.stderr)
            print("Install with: uv tool install repren", file=sys.stderr)
            print("", file=sys.stderr)
            print(
                "Alternative: Download SKILL.md directly from the repository:",
                file=sys.stderr,
            )
            print(
                "  curl https://raw.githubusercontent.com/jlevy/repren/master/repren/skills/SKILL.md",
                file=sys.stderr,
            )
            sys.exit(1)

    # Option setup.
    options.do_contents = not options.do_renames
    options.do_renames = options.do_renames or options.do_full

    global _fail
    _fail = _fail_with_exit
    # In JSON mode, suppress text output (JSON result will be output at end)
    json_mode = options.output_format == "json"
    log: LogFunc = print_stderr if not options.quiet and not json_mode else no_log

    # Validate backup suffix
    if not options.backup_suffix.startswith("."):
        parser.error("--backup-suffix must start with '.'")

    if options.walk_only:
        paths, skipped_backup_count = walk_files(
            options.root_paths,
            include_pat=options.include_pat,
            exclude_pat=options.exclude_pat,
            backup_suffix=options.backup_suffix,
        )
        if json_mode:
            _output_json(
                {
                    "operation": "walk",
                    "paths": paths,
                    "files_found": len(paths),
                    "skipped_backups": skipped_backup_count,
                }
            )
        else:
            if skipped_backup_count > 0:
                log(
                    f"Skipped {skipped_backup_count} file(s) ending in '{options.backup_suffix}' "
                    "(backup files are never processed)"
                )
            log(f"Found {len(paths)} files in: {', '.join(options.root_paths)}")
            for path in paths:
                log(f"- {path}")
        return  # We're done!

    # Handle --clean-backups mode (standalone, no patterns needed)
    if options.clean_backups:
        if options.pat_file or options.from_pat or options.to_pat:
            parser.error("--clean-backups cannot be used with --patterns or --from/--to")
        if len(options.root_paths) == 0:
            parser.error("--clean-backups requires paths to process")
        if options.dry_run:
            log("Dry run: No files will be changed")
        removed = clean_backups(
            options.root_paths,
            backup_suffix=options.backup_suffix,
            include_pat=options.include_pat,
            exclude_pat=options.exclude_pat,
            dry_run=options.dry_run,
            log=log,
        )
        if json_mode:
            _output_json(
                {
                    "operation": "clean_backups",
                    "dry_run": options.dry_run,
                    "removed": removed,
                }
            )
        else:
            action_word = "Would remove" if options.dry_run else "Removed"
            log(f"{action_word} {removed} backup file(s)")
        return  # We're done!

    # log("Settings: %s" % options)

    if options.pat_file:
        if options.from_pat or options.to_pat:
            parser.error("cannot use both --patterns and --from/--to")
    elif options.from_pat is None or options.to_pat is None:
        parser.error("must specify --patterns or both --from and --to")
    if options.insensitive and options.preserve_case:
        parser.error("cannot use --insensitive and --preserve-case at once")

    by_line = not options.at_once

    if options.pat_file:
        with open(options.pat_file, "rb") as f:
            pat_str = f.read().decode("utf-8")
    else:
        pat_str = f"{options.from_pat}\t{options.to_pat}"
    patterns = parse_patterns(
        pat_str,
        literal=options.literal,
        word_breaks=options.word_breaks,
        insensitive=options.insensitive,
        dotall=options.dotall,
        preserve_case=options.preserve_case,
    )

    if len(patterns) == 0:
        _fail("found no parse patterns", None)

    def format_flags(flags: int) -> str:
        flags_str = "|".join([s for s in ["IGNORECASE", "DOTALL"] if flags & getattr(re, s)])
        if flags_str:
            flags_str += " "
        return flags_str

    if options.dry_run:
        log("Dry run: No files will be changed")
    log(
        f"Using {len(patterns)} patterns:\n  "
        + "\n  ".join(
            f"'{safe_decode(regex.pattern)}' {format_flags(regex.flags)}-> '{safe_decode(replacement)}'"
            for (regex, replacement) in patterns
        ),
    )

    if options.parse_only:
        return  # We're done!

    # Handle --undo mode
    if options.undo:
        if len(options.root_paths) == 0:
            parser.error("--undo requires paths to process")
        restored, skipped = undo_backups(
            options.root_paths,
            patterns,
            backup_suffix=options.backup_suffix,
            include_pat=options.include_pat,
            exclude_pat=options.exclude_pat,
            dry_run=options.dry_run,
            log=log,
        )
        if json_mode:
            _output_json(
                {
                    "operation": "undo",
                    "dry_run": options.dry_run,
                    "restored": restored,
                    "skipped": skipped,
                }
            )
        else:
            action_word = "Would restore" if options.dry_run else "Restored"
            log(f"{action_word} {restored} file(s), skipped {skipped} with warnings")
        return  # We're done!

    # Process files.
    if len(options.root_paths) > 0:
        rewrite_files(
            options.root_paths,
            patterns,
            do_renames=options.do_renames,
            do_contents=options.do_contents,
            exclude_pat=options.exclude_pat,
            include_pat=options.include_pat,
            backup_suffix=options.backup_suffix,
            by_line=by_line,
            dry_run=options.dry_run,
            log=log,
        )

        if json_mode:
            _output_json(
                {
                    "operation": "replace",
                    "dry_run": options.dry_run,
                    "patterns_count": len(patterns),
                    "files_found": _tally.files,
                    "chars_read": _tally.chars,
                    "matches_found": _tally.matches,
                    "matches_applied": _tally.valid_matches,
                    "files_changed": _tally.files_changed,
                    "files_rewritten": _tally.files_rewritten,
                    "files_renamed": _tally.renames,
                }
            )
        else:
            log(
                f"Read {_tally.files} files ({_tally.chars} chars), found {_tally.valid_matches} matches "
                f"({_tally.matches - _tally.valid_matches} skipped due to overlaps)",
            )
            change_words = "Dry run: Would have changed" if options.dry_run else "Changed"
            log(
                f"{change_words} {_tally.files_changed} files "
                f"({_tally.files_rewritten} rewritten and {_tally.renames} renamed)",
            )
    else:
        if options.do_renames:
            parser.error("can't specify --renames on stdin; give filename arguments")
        if options.dry_run:
            parser.error("can't specify --dry-run on stdin; give filename arguments")
        if json_mode:
            parser.error("can't specify --format json on stdin; give filename arguments")
        transform = lambda contents: multi_replace(contents, patterns, log=log)
        transform_stream(transform, sys.stdin.buffer, sys.stdout.buffer, by_line=by_line)

        log(
            f"Read {_tally.chars} chars, made {_tally.valid_matches} replacements "
            f"({_tally.matches - _tally.valid_matches} skipped due to overlaps)",
        )


def main() -> None:
    """CLI entrypoint with centralized error handling."""
    try:
        _run_cli()
    except CLIError as e:
        print(f"error: {e.message}", file=sys.stderr)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(EXIT_INTERRUPTED)


if __name__ == "__main__":
    main()

# TODO:
#   consider using regex for better Unicode support (but only gracefully, such as
#     with a dynamic import, if those features like Unicode character properties are needed)
#   Log collisions
#   Separate patterns file for renames and replacements
#   Should --at-once be the default?
