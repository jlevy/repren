# repren

![But call me repren for short](https://github.com/jlevy/repren/blob/master/images/awkward-150.jpg)

* * *

✨ **NEW:** [v2.0.0-rc1](https://github.com/jlevy/repren/releases/tag/2.0.0-rc1) is out,
refreshed for agent-friendly use and Python 3.10-3.14! ✨

* * *

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

Aren’t there standard tools for this already?

It’s a bit surprising, but not really.
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

repren includes a built-in skill for [Claude Code](https://claude.com/claude-code),
making it easy for Claude AI to use repren for bulk refactoring tasks.

**Quick Install:**

```bash
# Install globally (default, available in all projects)
uvx repren --install-skill

# Or: Install for current project only (shareable with team via git)
uvx repren --install-skill --install-dir=.
```

By default, the skill installs globally to `~/.claude/skills/repren`. Use
`--install-dir=.` to install in the current directory’s `.claude/skills/repren` instead.

Once installed, Claude Code will automatically use repren for bulk refactoring tasks.

**Manual Installation:**

To view the skill content for manual installation, run:

```bash
uvx repren --skill
```

Then save the output to `~/.claude/skills/repren/SKILL.md` (global) or
`.claude/skills/repren/SKILL.md` (project).

**Learn More:** See the [Claude Code documentation](https://code.claude.com/) and
[Agent Skills repository](https://github.com/anthropics/skills).

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

## Contributing

Contributions and issues welcome!
Check the output of the test script and if it has changed or needs updating, and commit
the clean log changes if you submit a PR.

## License

MIT.
