# repren

![But call me repren for short](https://github.com/jlevy/repren/blob/master/images/awkward-150.jpg)

* * *

> [!TIP]
> ✨✨ **Using a coding agent?** Just tell Claude Code, Codex, Gemini, or any agent:
>
> > Run `uvx repren@latest --help` and follow the instructions to install repren as a skill.
>
> That’s the whole setup. The agent reads repren’s self-documenting `--help`, installs
> the skill, and from then on reaches for repren automatically on bulk refactors and
> renames. See [Agent Use](#agent-use) for details.

> [!TIP]
> 🔒 **Zero dependencies.** repren has **zero runtime dependencies** — just Python and a
> single file. Amid the rise of supply-chain attacks on package ecosystems, that means
> there’s no transitive dependency tree to audit or be compromised: the only code `uvx
> repren@latest` ever fetches and runs is repren itself, and you (or your agent) can review
> its security before trusting it.

* * *

## Rename Anything

`repren` is a powerful CLI string replacement and file renaming tool for use by agents
or humans for almost any search-and-replace or renaming task.

It is small, self-contained, self-documenting, and works on Python 3.10-3.14 with
**zero runtime dependencies**. Essentially, it is a general-purpose, brute-force text
file refactoring tool.

**Using a coding agent?** This is the whole setup — tell Claude Code, Codex, Gemini, or
any agent:

> Run `uvx repren@latest --help` and follow the instructions to install repren as a skill.

repren’s `--help` ends with the exact install commands, so the agent reads them and takes
it from there. After that it reaches for repren automatically on bulk refactors and
renames. (See [Agent Use](#agent-use).)

**Zero dependencies, by design.** Given the rise of supply-chain attacks on package
ecosystems, it’s worth noting that repren has **zero runtime dependencies** — installing
it (or running `uvx repren@latest`) pulls in nothing but repren itself and the Python
standard library. There is no transitive dependency tree to audit or to be compromised,
so it is simpler and safer to adopt than most tools. It’s also a single file you can read
end to end (or have your agent review) before you trust it. The dev-only tooling used to
build and test repren (pytest, ruff, etc.) is never installed when you use it.

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

## Comparison to Alternatives

There are many tools for search/replace and refactoring.
Here’s how repren compares:

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

- **repren**: Bulk renames with file/directory renaming, case preservation, or
  simultaneous swaps. Works on any text file with full backup/undo support.
- **sed/awk/perl**: Classic approaches for quick one-liners.
  See
  [classic approaches](http://stackoverflow.com/questions/11392478/how-to-replace-a-string-in-multiple-files-in-linux-command-line/29191549).
  Often error-prone for complex patterns and lack dry-run mode, simultaneous swaps, or
  cross-platform consistency.
- **sd**: Fast sed replacement (2-11x faster than sed), but limited to simple
  find/replace without file renaming, case preservation, or multi-pattern swaps.
- **fastmod**: Good for interactive human review of changes, but lacks case
  preservation, simultaneous swaps, and file/directory renaming.
- **ast-grep**: Language-aware refactoring where you need to match code structure (e.g.,
  function calls, not just text).
  Use when semantic understanding matters more than speed.
- **comby**: Structural matching across languages without learning AST syntax.
  Useful when you need to match code patterns like balanced braces, but overkill for
  simple text refactoring.
- **rnr**: File/directory renaming only (no content replacement).
  Has dry-run by default, backup option, and undo via dump files.
  Use repren if you also need content replacement.

## Installation

repren has **zero runtime dependencies** (just Python 3.10+), so installing it never adds
a transitive dependency tree to your environment. It’s easiest to install with
[uv](https://docs.astral.sh/uv/):

```bash
# Install as a tool:
uv tool install repren

# Or run directly without installing:
uvx repren@latest --help
```

Or, since it’s just one file, you can copy the
[repren.py](https://raw.githubusercontent.com/jlevy/repren/master/repren/repren.py)
script somewhere convenient and make it executable.

**A note on freshness and safety.** These examples use `@latest` for simplicity. Because
repren has **zero runtime dependencies**, the only code fetched and run is repren itself —
there is no transitive dependency tree to audit or be compromised — so `@latest` carries
far less supply-chain risk here than for a typical package. If you want an extra safety
margin, you can opt into uv’s release “cool-off” (which excludes very recent uploads), or
pin an exact version:

```bash
# Skip uploads newer than 14 days, then run the latest within that window:
UV_EXCLUDE_NEWER="14 days" uvx repren@latest --help

# Or pin an exact version:
uvx repren@2.0.0 --help
```

## Agent Use

**The one thing to know:** point your agent at repren’s self-documenting help and let it
install itself —

> Run `uvx repren@latest --help` and follow the instructions to install repren as a skill.

repren’s `--help` ends with the exact install commands, so the agent can take it from
there. (`uvx` runs repren with no prior install; see the note on `@latest` and safety
under [Installation](#installation).)

**Install the skill yourself** (the same thing the agent does):

```bash
# Install into the current project (run from the repo; shareable via git):
uvx repren@latest --install-skill --project

# Or install globally, for every project:
uvx repren@latest --install-skill --global
```

Re-run any time to update an existing install.

### How it works

repren is **self-documenting**: `repren --help` and `repren --docs` are the source of
truth for every flag, and `--format=json` gives agents machine-parseable output. The
skill is just a thin pointer to those commands, so it never drifts out of date.

Installing the skill writes one `SKILL.md` to **both** discovery locations, so every
agent finds it:

- `.agents/skills/repren/` — the portable, cross-agent location (Codex, Gemini, pi, …)
- `.claude/skills/repren/` — the Claude Code mirror

repren is a general-purpose utility with no per-project config, so the skill invokes it
through the zero-install runner `uvx repren@latest` — there’s no need to add repren as a
project dependency. Because repren has **zero runtime dependencies**, the only code a
runner ever fetches and runs is repren itself; for an extra safety margin you can opt into
uv’s release cool-off (`UV_EXCLUDE_NEWER`, see [Installation](#installation)) in your
environment, which applies to the skill’s invocations too.

**Scope is resolved like `git config`** — implicit when unambiguous, a clear error when
not — so a stray `--install-skill` never silently rewrites your global agent surfaces:

- Inside a git repo, `--project` is implied (so `uvx repren --install-skill` just works).
- In an ambiguous spot (your home directory, or outside any repo) repren refuses and
  tells you to pass `--project` (optionally with `--dir DIR` or `--no-repo-check`) or
  `--global`.

**Manual install:** run `uvx repren --skill` and save the output to
`.agents/skills/repren/SKILL.md` (and/or `.claude/skills/repren/SKILL.md`), under `~` for
a global install or the project root for a project install.

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

- By default, recursive searching omits paths starting with “.” (including `.git/`). This
  may be adjusted with `--exclude`. Files ending in the backup suffix (`.orig` by default)
  are always ignored. repren does **not** read `.gitignore`: any other paths you want to
  skip — `node_modules/`, `build/`, `dist/`, vendored code — must be named explicitly with
  `--exclude`, and richer scoping is done with `--include`/`--exclude` (preview with
  `--dry-run`).

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
