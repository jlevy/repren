#!/usr/bin/env python
"""
## Rename Anything

Repren is a simple but flexible command-line tool for rewriting file contents according
to a set of regular expression patterns, and to rename or move files according to
patterns. Essentially, it is a general-purpose, brute-force text file refactoring tool.

For example, repren could rename all occurrences of certain class and variable names in
a set of Java source files, while simultaneously renaming the Java files according to
the same pattern.

It's more powerful than usual options like `perl -pie`, `rpl`, or `sed`:

- It can also rename files, including moving files and creating directories.

- It supports fully expressive regular expression substitutions.

- It performs group renamings, i.e. rename "foo" as "bar", and "bar" as "foo" at once,
  without requiring a temporary intermediate rename.

- It is careful. It has a nondestructive mode, and prints clear stats on its changes.
  It leaves backups. File operations are done atomically, so interruptions never leave a
  previously existing file truncated or partly edited.

- It supports "magic" case-preserving renames that let you find and rename identifiers
  with case variants (lowerCamel, UpperCamel, lower_underscore, and UPPER_UNDERSCORE)
  consistently.

- It has this nice documentation!

If file paths are provided, repren replaces those files in place, leaving a backup with
extension ".orig".

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
figure ([0-9+])<tab>Figure \\1
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
repren -p patfile < input > output

# Shortcut with a single pattern replacement (replace foo with bar):
repren --from foo --to bar < input > output

# Rewrite a few files in place, also requiring matches be on word breaks:
repren -p patfile --word-breaks myfile1 myfile2 myfile3

# Rewrite whole directory trees. Since this is a big operation, we use
# `-n` to do a dry run that only prints what would be done:
repren -n -p patfile --word-breaks --full mydir1

# Now actually do it:
repren -p patfile --word-breaks --full mydir1

# Same as above, for all case variants:
repren -p patfile --word-breaks --preserve-case --full mydir1

# Same as above but including only .py files and excluding the tests directory
# and any files or directories starting with test_:
repren -p patfile --word-breaks --preserve-case --full --include='.*[.]py$' --exclude='tests|test_.*' mydir1
```

## Usage

Run `repren --help` for full usage and flags.

If file paths are provided, repren replaces those files in place, leaving a backup with
extension ".orig". If directory paths are provided, it applies replacements recursively
to all files in the supplied paths that are not in the exclude pattern.
If no arguments are supplied, it reads from stdin and writes to stdout.

## Alternatives

Aren't there standard tools for this already?

It's a bit surprising, but not really.
Getting the features right is a bit tricky, I guess.
The
[standard](http://stackoverflow.com/questions/11392478/how-to-replace-a-string-in-multiple-files-in-linux-command-line/29191549)
[answers](http://stackoverflow.com/questions/6840332/rename-multiple-files-by-replacing-a-particular-pattern-in-the-filenames-using-a)
like *sed*, *perl*, *awk*, *rename*, *Vim* macros, or even IDE refactoring tools, often
cover specific cases, but tend to be error-prone or not offer specific features you
probably want. Things like nondestructive mode, file renaming as well as search/replace,
multiple simultaneous renames/swaps, or renaming enclosing parent directories.
Also many of these vary by platform, which adds to the corner cases.
Inevitably you end up digging through the darker corners of a man page, doing
semi-automated things in an IDE, or writing hacked scripts that are an embarrassment to
share.

## Installation

No dependencies except Python 3.10+. It's easiest to install with pip:

```bash
pip install repren
```

Or, since it's just one file, you can copy the
[repren.py](https://raw.githubusercontent.com/jlevy/repren/master/repren/repren.py)
script somewhere convenient and make it executable.

## Try It

Let's try a simple replacement in my working directory (which has a few random source
files):

```bash
$ repren --from frobinator-server --to glurp-server --full --dry-run .
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

That was a dry run, so if it looks good, it's easy to repeat that a second time,
dropping the `--dry-run` flag.
If this is in git, we'd do a git diff to verify, test, then commit it all.
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
repren -p patfile < input > output

# Shortcut with a single pattern replacement (replace foo with bar):
repren --from foo --to bar < input > output

# Rewrite a few files in place, also requiring matches be on word breaks:
repren -p patfile --word-breaks myfile1 myfile2 myfile3

# Rewrite whole directory trees. Since this is a big operation, we use
# `-n` to do a dry run that only prints what would be done:
repren -n -p patfile --word-breaks --full mydir1

# Now actually do it:
repren -p patfile --word-breaks --full mydir1

# Same as above, for all case variants:
repren -p patfile --word-breaks --preserve-case --full mydir1
```

## Notes

- All pattern matching is via standard
  [Python regular expressions](https://docs.python.org/3/library/re.html).

- As with sed, replacements are made line by line by default.
  Memory permitting, replacements may be done on entire files using `--at-once`.

- As with sed, replacement text may include backreferences to groups within the regular
  expression, using the usual syntax: \\1, \\2, etc.

- In the pattern file, both the regular expression and the replacement may contain the
  usual escapes `\\n`, `\\t`, etc.
  (To match a multi-line pattern, containing `\\n`, you must must use `--at-once`.)

- Replacements are all matched on each input file, then all replaced, so it's possible
  to swap or otherwise change names in ways that would require multiple steps if done
  one replacement at at a time.

- If two patterns have matches that overlap, only one replacement is applied, with
  preference to the pattern appearing first in the patterns file.

- If one pattern is a subset of another, consider if `--word-breaks` will help.

- If patterns have special characters, `--literal` may help.

- The case-preserving option works by adding all case variants to the pattern
  replacements, e.g. if the pattern file has foo_bar -> xxx_yyy, the replacements fooBar
  -> xxxYyy, FooBar -> XxxYyy, FOO_BAR -> XXX_YYY are also made.
  Assumes each pattern has one casing convention.

- The same logic applies to filenames, with patterns applied to the full file path with
  slashes replaced and then and parent directories created as needed, e.g.
  `my/path/to/filename` can be rewritten to `my/other/path/to/otherfile`. (Use caution
  and test with `-n`, especially when using absolute path arguments!)

- Files are never clobbered by renames.
  If a target already exists, or multiple files are renamed to the same target, numeric
  suffixes will be added to make the files distinct (".1", ".2", etc.).

- Files are created at a temporary location, then renamed, so original files are left
  intact in case of unexpected errors.
  File permissions are preserved.

- Backups are created of all modified files, with the suffix ".orig".

- By default, recursive searching omits paths starting with ".". This may be adjusted
  with `--exclude`. Files ending in `.orig` are always ignored.

- Data is handled as bytes internally, allowing it to work with any encoding or binary
  files. File contents are not decoded unless necessary (e.g., for logging).
  However, patterns are specified as strings in the pattern file and command line
  arguments, and file paths are handled as strings for filesystem operations.

"""


import argparse
import bisect
import importlib.metadata
import os
import re
import shutil
import sys
from dataclasses import dataclass
from typing import BinaryIO, Callable, List, Match, Optional, Pattern, Tuple

# Type aliases for clarity.
PatternType = Tuple[Pattern[bytes], bytes]
FileHandle = BinaryIO
MatchType = Match[bytes]
PatternPair = Tuple[MatchType, bytes]
TransformFunc = Callable[[bytes], Tuple[bytes, "_MatchCounts"]]
LogFunc = Callable[[str], None]
FailHandler = Callable[[str, Optional[Exception]], None]

# Get the version from package metadata.
VERSION: str
try:
    VERSION = importlib.metadata.version("repren")
except importlib.metadata.PackageNotFoundError:
    # Fallback version if package metadata is not available.
    VERSION = "0.0.0.dev"

DESCRIPTION: str = "repren: Multi-pattern string replacement and file renaming"

BACKUP_SUFFIX: str = ".orig"
TEMP_SUFFIX: str = ".repren.tmp"
DEFAULT_EXCLUDE_PAT: str = r"^\."

CONSOLE_WIDTH: int = 88


def no_log(msg: str) -> None:
    pass


def print_stderr(msg: str) -> None:
    print(msg, file=sys.stderr)


def _fail_exit(msg: str, e: Optional[Exception] = None) -> None:
    if e:
        msg = "%s: %s" % (msg, e) if msg else str(e)
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def _fail_exception(msg: str, e: Optional[Exception] = None) -> None:
    raise ValueError(msg) from e


# By default, fail with exceptions in case we want to use this as a library.
_fail: FailHandler = _fail_exception


def safe_decode(b: bytes) -> str:
    """
    Safely decode bytes to a string for logging purposes.
    Replaces invalid UTF-8 sequences to prevent errors.
    """
    return b.decode("utf-8", errors="backslashreplace")


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


# --- String matching ---


def _overlap(match1: MatchType, match2: MatchType) -> bool:
    return match1.start() < match2.end() and match2.start() < match1.end()


def _sort_drop_overlaps(
    matches: List[PatternPair],
    source_name: Optional[str] = None,
    log: LogFunc = no_log,
) -> List[PatternPair]:
    """Select and sort a set of disjoint intervals, omitting ones that overlap."""
    non_overlaps: List[PatternPair] = []
    starts: List[int] = []
    for match, replacement in matches:
        index: int = bisect.bisect_left(starts, match.start())
        if index > 0:
            (prev_match, _) = non_overlaps[index - 1]
            if _overlap(prev_match, match):
                log(
                    "- %s: Skipping overlapping match '%s' of '%s' that overlaps '%s' of '%s' on its left"
                    % (
                        source_name,
                        safe_decode(match.group()),
                        safe_decode(match.re.pattern),
                        safe_decode(prev_match.group()),
                        safe_decode(prev_match.re.pattern),
                    ),
                )
                continue
        if index < len(non_overlaps):
            (next_match, _) = non_overlaps[index]
            if _overlap(next_match, match):
                log(
                    "- %s: Skipping overlapping match '%s' of '%s' that overlaps '%s' of '%s' on its right"
                    % (
                        source_name,
                        safe_decode(match.group()),
                        safe_decode(match.re.pattern),
                        safe_decode(next_match.group()),
                        safe_decode(next_match.re.pattern),
                    ),
                )
                continue
        starts.insert(index, match.start())
        non_overlaps.insert(index, (match, replacement))
    return non_overlaps


def _apply_replacements(input_bytes: bytes, matches: List[PatternPair]) -> bytes:
    out: List[bytes] = []
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

    def add(self, o: "_MatchCounts") -> None:
        self.found += o.found
        self.valid += o.valid


def multi_replace(
    input_bytes: bytes,
    patterns: List[PatternType],
    is_path: bool = False,
    source_name: Optional[str] = None,
    log: LogFunc = no_log,
) -> Tuple[bytes, _MatchCounts]:
    """
    Replace all occurrences in the input given a list of patterns (regex,
    replacement), simultaneously, so that no replacement affects any other.
    """
    matches: List[PatternPair] = []
    for regex, replacement in patterns:
        for match in regex.finditer(input_bytes):
            matches.append((match, replacement))
    valid_matches: List[PatternPair] = _sort_drop_overlaps(
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


def _split_name(name: str) -> Tuple[str, List[str]]:
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
    separator, words = _split_name(name)
    return words[0].lower() + "".join(_capitalize(word) for word in words[1:])


def to_upper_camel(name: str) -> str:
    separator, words = _split_name(name)
    return "".join(_capitalize(word) for word in words)


def to_lower_underscore(name: str) -> str:
    separator, words = _split_name(name)
    return "_".join(word.lower() for word in words)


def to_upper_underscore(name: str) -> str:
    separator, words = _split_name(name)
    return "_".join(word.upper() for word in words)


def _transform_expr(expr: str, transform: Callable[[str], str]) -> str:
    transformed = _name_pat.sub(lambda m: transform(m.group()), expr)
    return transformed


def all_case_variants(expr: str) -> List[str]:
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
            dest_path = "%s.%s" % (dest_path, i)
            i += 1
    shutil.move(source_path, dest_path)


def transform_stream(
    transform: Optional[TransformFunc],
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
        stream_out.write(new_contents)
    return counts


def transform_file(
    transform: Optional[TransformFunc],
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
    patterns: List[PatternType],
    do_renames: bool = False,
    do_contents: bool = False,
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
    counts = transform_file(transform, path, dest_path, by_line=by_line, dry_run=dry_run)
    if counts.found > 0:
        log("- modify: %s: %s matches" % (path, counts.found))
    if dest_path != path:
        log("- rename: %s -> %s" % (path, dest_path))


def walk_files(
    paths: List[str],
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
) -> List[str]:
    include_re = re.compile(include_pat)
    exclude_re = re.compile(exclude_pat)
    out: List[str] = []

    for path in paths:
        if os.path.isfile(path):
            f = os.path.basename(path)
            if include_re.match(f) and not exclude_re.match(f):
                out.append(path)
        else:
            for root, dirs, files in os.walk(path):
                # Filter directories based on include and exclude patterns
                dirs[:] = [d for d in dirs if not exclude_re.match(d)]
                for f in files:
                    if (
                        include_re.match(f)
                        and not exclude_re.match(f)
                        and not f.endswith(BACKUP_SUFFIX)
                        and not f.endswith(TEMP_SUFFIX)
                    ):
                        out.append(os.path.join(root, f))

    out.sort()  # Ensure deterministic order of file processing.
    return out


def rewrite_files(
    root_paths: List[str],
    patterns: List[PatternType],
    do_renames: bool = False,
    do_contents: bool = False,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    by_line: bool = False,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> None:
    """
    Walk the given `root_paths`, rewriting and/or renaming files making simultaneous
    changes according to the given list of patterns. Set `log` if you wish to log info
    in `dry_run` mode.
    """
    paths = walk_files(
        root_paths,
        include_pat=include_pat,
        exclude_pat=exclude_pat,
    )
    log("Found %s files in: %s" % (len(paths), ", ".join(root_paths)))
    for path in paths:
        rewrite_file(
            path,
            patterns,
            do_renames=do_renames,
            do_contents=do_contents,
            by_line=by_line,
            dry_run=dry_run,
            log=log,
        )


# --- Invocation ---


def parse_patterns(
    patterns_str: str,
    literal: bool = False,
    word_breaks: bool = False,
    insensitive: bool = False,
    dotall: bool = False,
    preserve_case: bool = False,
) -> List[PatternType]:
    patterns: List[PatternType] = []
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
                pairs: List[Tuple[str, str]] = []
                if preserve_case:
                    pairs += zip(all_case_variants(regex), all_case_variants(replacement))
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
            _fail("error parsing pattern: %s: %s" % (e, bits), e)
    return patterns


def main() -> None:
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog=prog, width=CONSOLE_WIDTH
        ),
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="show usage and help page",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="show program's version number and exit",
    )
    parser.add_argument(
        "--usage",
        help="show usage",
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
        help="file or directory name regex to exclude ()",
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
    parser.add_argument("root_paths", nargs="*", help="root paths to process")

    if "--usage" in sys.argv:
        parser.print_help()
        sys.exit(0)

    # For full --help, add the complete documentation.
    parser.epilog = __doc__

    options = parser.parse_args()

    # Option setup.
    options.do_contents = not options.do_renames
    options.do_renames = options.do_renames or options.do_full

    global _fail
    _fail = _fail_exit
    log: LogFunc = print_stderr if not options.quiet else no_log

    if options.walk_only:
        paths = walk_files(
            options.root_paths, include_pat=options.include_pat, exclude_pat=options.exclude_pat
        )
        log("Found %s files in: %s" % (len(paths), ", ".join(options.root_paths)))
        for path in paths:
            log("- %s" % path)
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
        pat_str = "%s\t%s" % (options.from_pat, options.to_pat)
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
        ("Using %s patterns:\n  " % len(patterns))
        + "\n  ".join(
            [
                "'%s' %s-> '%s'"
                % (
                    safe_decode(regex.pattern),
                    format_flags(regex.flags),
                    safe_decode(replacement),
                )
                for (regex, replacement) in patterns
            ]
        ),
    )

    if options.parse_only:
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
            by_line=by_line,
            dry_run=options.dry_run,
            log=log,
        )

        log(
            "Read %s files (%s chars), found %s matches (%s skipped due to overlaps)"
            % (
                _tally.files,
                _tally.chars,
                _tally.valid_matches,
                _tally.matches - _tally.valid_matches,
            ),
        )
        change_words = "Dry run: Would have changed" if options.dry_run else "Changed"
        log(
            "%s %s files (%s rewritten and %s renamed)"
            % (change_words, _tally.files_changed, _tally.files_rewritten, _tally.renames),
        )
    else:
        if options.do_renames:
            parser.error("can't specify --renames on stdin; give filename arguments")
        if options.dry_run:
            parser.error("can't specify --dry-run on stdin; give filename arguments")
        transform = lambda contents: multi_replace(contents, patterns, log=log)
        transform_stream(transform, sys.stdin.buffer, sys.stdout.buffer, by_line=by_line)

        log(
            "Read %s chars, made %s replacements (%s skipped due to overlaps)"
            % (_tally.chars, _tally.valid_matches, _tally.matches - _tally.valid_matches),
        )


if __name__ == "__main__":
    main()

# TODO:
#   consider using regex for better Unicode support (but only gracefully, such as
#     with a dynamic import, if those features like Unicode character properties are needed)
#   --undo mode to revert a previous run by using .orig files
#   --clean mode to remove .orig files
#   --orig_suffix to allow for backups besides .orig, including for these use cases
#   Log collisions
#   Separate patterns file for renames and replacements
#   Should --at-once be the default?
