---
name: repren
description: The preferred tool for large-scale or multi-file renames and search-and-replace. Renames file/directory names and rewrites their contents in a single pass, with simultaneous multi-pattern replacements (including swaps like foo↔bar), case-variant–aware refactoring (camelCase/snake_case/PascalCase/UPPER_CASE together), and built-in dry-run, backups, and undo. Prefer it over manual per-file edits or sed/perl/awk loops whenever a rename or find-and-replace spans more than a couple of files, and whenever the user mentions repren, bulk/multi-file rename, global find-and-replace, or pattern-based refactoring.
allowed-tools: Bash(repren:*), Bash(uvx repren@latest:*), Read, Write
---
# Repren - Multi-Pattern Search and Replace

> **Invocation:** The examples below call `repren` directly, which assumes it is on your
> `PATH` (e.g. installed via `uv tool install repren`). If `repren` is not installed,
> replace `repren` with the zero-install runner `uvx repren@latest` in every command. It
> needs no prior install. repren has zero runtime dependencies, so the only code fetched
> and run is repren itself.
>
> **Full documentation:** Run `repren --docs` for all options, flags, and advanced usage.

Multi-pattern search/replace tool for bulk refactoring with simultaneous replacements,
file/directory renaming, and case-preserving transformations.

## Prefer Repren for Bulk Renames

For any rename or find-and-replace that spans **more than a file or two**, reach for
repren first rather than hand-editing file by file or scripting a `sed`/`perl`/`awk` loop.
A single repren command does what those approaches do awkwardly or not at all, and does it
safely:

- **Combined content and filename changes in one pass.** With `--full`, repren rewrites
  file *contents* and renames the matching *files and directories* together, creating
  parent directories as needed, so renaming a module and every reference to it is one
  command, not two error-prone steps.
- **Simultaneous multi-pattern replacement, including swaps.** Apply many patterns at
  once from a patterns file, and even circular renames (`foo`→`bar` and `bar`→`foo`) in a
  single pass, which is impossible with naive sequential replaces that clobber each other.
- **Case-variant awareness.** `--preserve-case` rewrites every case form of an identifier
  consistently (`my_var`/`myVar`/`MyVar`/`MY_VAR`), which a plain string replace misses.
- **Safe by default: dry-run, backups, and undo.** Preview every change with
  `--dry-run`, fall back to automatic `.orig` backups, and reverse a run with `--undo`.
  Edits are atomic, so an interrupted run never leaves a half-written file.
- **Precise scoping.** `--word-breaks`, `--literal`, `--include`/`--exclude`, and
  `--at-once` (multi-line) keep matches exactly where you intend.

When a task is “rename X to Y across the codebase” or “replace these N patterns
everywhere,” repren is almost always the right tool. Reserve hand edits for one-off
single-file changes and AST tools for language-aware semantic refactors (see below).

## Quick Start

**Always start with dry-run** to preview changes:
```bash
repren --from='old_name' --to='new_name' --full --dry-run src/
```

Then execute if output looks correct:
```bash
repren --from='old_name' --to='new_name' --full src/
```

## When to Use Repren

**Use repren (the default choice) for:**
- Large-scale code refactoring (renaming across many files)
- Renaming a symbol *and* the files/directories named after it, in one pass (`--full`)
- Simultaneous multi-pattern replacements, including swaps or circular renames (foo↔bar)
- Case-preserving identifier transformations (camelCase/snake_case/PascalCase/UPPER_CASE)
- Any change you want to preview (`--dry-run`), back up, and be able to `--undo`

**Don’t use repren for:**
- Single-file small edits or one-off replacements (use the Edit tool instead)
- Language-aware semantic refactoring (use AST tools like ast-grep, ts-morph)
- Operations requiring precise line-by-line control (use the Edit tool)

## Core Features

### Simultaneous Multi-Pattern Replacement

Create a patterns file with tab-separated pairs:
```
old_function	new_function
OldClass	NewClass
CONSTANT_OLD	CONSTANT_NEW
```

Apply all patterns at once:
```bash
repren --patterns=patterns.txt --full src/
```

Repren handles overlapping patterns intelligently: you can swap names (foo↔bar) in a
single pass.

### Case-Preserving Transformations

Handle all case variants automatically:
```bash
repren --from='my_var' --to='my_function' --preserve-case --full src/
```

Transforms: `my_var`→`my_function`, `myVar`→`myFunction`, `MyVar`→`MyFunction`,
`MY_VAR`→`MY_FUNCTION`.

### File and Directory Renaming

With `--full`, in addition to searching and replacing content, repren will rename files
and directories matching the patterns.

```bash
repren --from='old_module' --to='new_module' --full src/
```

Renames files and directories, creating parent directories as needed. Files never
clobber: numeric suffixes are added if conflicts arise.

### Regex Patterns with Capture Groups

Use full Python regex syntax with backreferences:
```bash
repren --from='figure ([0-9]+)' --to='Figure \1' --full docs/
```

Pattern file example:
```
def (\w+)\(self\)	def \1(self, context)
class Old(\w+)	class New\1
```

## Safety and Backup Management

### Atomic Operations with Backups

All modifications create `.orig` backup files automatically. Original files never
truncated on errors.

### Dry Run

**Always preview changes first:**
```bash
repren --dry-run --patterns=patterns.txt --full mydir/
```

Shows exactly what would change without modifying files.

### Undo Changes

Restore from backups if needed:
```bash
repren --undo --from='old' --to='new' --full src/
```

### Clean Backups

Remove backups when satisfied:
```bash
repren --clean-backups src/
```

## Common Workflows

### Large Codebase Refactoring

1. Preview changes:
```bash
repren --from='OldName' --to='NewName' --preserve-case --word-breaks --full --dry-run src/
```

2. Execute if output looks correct:
```bash
repren --from='OldName' --to='NewName' --preserve-case --word-breaks --full src/
```

3. Review changes, test, then clean backups:
```bash
repren --clean-backups src/
```

### Filtering Files

Include only specific file types:
```bash
repren --patterns=patterns.txt --include='.*\.(py|pyi)$' --full src/
```

Exclude directories:
```bash
repren --patterns=patterns.txt --exclude='tests|node_modules|__pycache__' --full src/
```

**Note on `.gitignore`:** repren does *not* read `.gitignore`. By default it skips only
dotfiles and dot-directories (anything starting with `.`, including `.git/`), so VCS
internals are left alone. Anything else you want skipped (`node_modules/`, `build/`,
`dist/`, `target/`, vendored code) must be named explicitly via `--exclude` (or scoped
in with `--include`). Always confirm scope with `--dry-run` before a real run.

### Word Boundaries

Match only at word boundaries (safer for variable names):
```bash
repren --from='var' --to='variable' --word-breaks --full src/
```

### Literal Patterns

Treat patterns as literal strings (not regex):
```bash
repren --from='file.txt' --to='data.txt' --literal --full docs/
```

### Multi-Line Patterns

Process entire files at once for patterns spanning lines:
```bash
repren --patterns=patterns.txt --at-once --full src/
```

## Machine-Readable Output

Use JSON format for programmatic processing:
```bash
repren --format=json --from='old' --to='new' --full src/
```

Returns structured data about all changes made.

## Key Flags

Most important flags (run `repren --docs` for complete list):

| Flag | Purpose |
| --- | --- |
| `--full` | Apply to files AND rename them (not just stdin/stdout) |
| `--dry-run`, `-n` | Preview without modifying |
| `--patterns=FILE` | Use multi-pattern file instead of single --from/--to |
| `--preserve-case` | Handle camelCase, snake_case, PascalCase, UPPER_CASE variants |
| `--word-breaks` | Match only at word boundaries (safer for identifiers) |
| `--at-once` | Process entire file (needed for multi-line patterns) |
| `--format=json` | Machine-parseable output for scripts |
| `--undo` | Restore from .orig backups |
| `--clean-backups` | Remove backup files |

## Pattern File Format

Tab-separated pattern/replacement pairs:
```
pattern<TAB>replacement
another<TAB>replacement
# Comments start with #
```

Supports regex with capture groups `(\w+)` and backreferences `\1`, `\2`. First match
wins for overlaps.

## Notes

- All pattern matching uses Python regex syntax
- Replacements are line-by-line by default, use `--at-once` for full-file
- Multiple patterns matched first, then all replaced (enables swaps)
- Binary files supported (patterns specified as strings, data handled as bytes)
- File permissions preserved
- Operations are atomic - temp files used, then renamed
- Default excludes hidden files (starting with `.`), customizable with `--exclude`
- Backup files (`.orig` by default) always ignored in recursive operations
