---
name: repren
description: Performs simultaneous multi-pattern search-and-replace, file/directory renaming, and case-preserving refactoring across codebases. Use for bulk refactoring, global find-and-replace, or when user mentions repren, multi-file rename, or pattern-based transformations.
allowed-tools: Bash(repren:*), Bash(uvx repren@latest:*), Read, Write
---
# Repren - Multi-Pattern Search and Replace

> **Full documentation: Run `uvx repren@latest --docs` for all options, flags, and advanced
> usage.**

Multi-pattern search/replace tool for bulk refactoring with simultaneous replacements,
file/directory renaming, and case-preserving transformations.

## Quick Start

**Always start with dry-run** to preview changes:
```bash
uvx repren@latest --from='old_name' --to='new_name' --full --dry-run src/
```

Then execute if output looks correct:
```bash
uvx repren@latest --from='old_name' --to='new_name' --full src/
```

## When to Use Repren

**Use repren for:**
- Large-scale code refactoring (renaming across many files)
- Simultaneous multi-pattern replacements
- File and directory renaming based on content patterns
- Case-preserving identifier transformations
- Operations requiring dry-run validation and backups
- Swapping or circular renames (foo↔bar)

**Don’t use repren for:**
- Single-file small edits or replacements (use Edit tool instead)
- Language-aware semantic refactoring (use AST tools like ast-grep, ts-morph)
- Operations requiring precise line-by-line control (use Edit tool)

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
uvx repren@latest --patterns=patterns.txt --full src/
```

Repren handles overlapping patterns intelligently: you can swap names (foo↔bar) in a
single pass.

### Case-Preserving Transformations

Handle all case variants automatically:
```bash
uvx repren@latest --from='my_var' --to='my_function' --preserve-case --full src/
```

Transforms: `my_var`→`my_function`, `myVar`→`myFunction`, `MyVar`→`MyFunction`,
`MY_VAR`→`MY_FUNCTION`.

### File and Directory Renaming

With `--full`, in addition to searching and replacing content, repren will rename files
and directories matching the patterns.

```bash
uvx repren@latest --from='old_module' --to='new_module' --full src/
```

Renames files and directories, creating parent directories as needed.
Files never clobber: numeric suffixes are added if conflicts arise.

### Regex Patterns with Capture Groups

Use full Python regex syntax with backreferences:
```bash
uvx repren@latest --from='figure ([0-9]+)' --to='Figure \1' --full docs/
```

Pattern file example:
```
def (\w+)\(self\)	def \1(self, context)
class Old(\w+)	class New\1
```

## Safety and Backup Management

### Atomic Operations with Backups

All modifications create `.orig` backup files automatically.
Original files never truncated on errors.

### Dry Run

**Always preview changes first:**
```bash
uvx repren@latest --dry-run --patterns=patterns.txt --full mydir/
```

Shows exactly what would change without modifying files.

### Undo Changes

Restore from backups if needed:
```bash
uvx repren@latest --undo --from='old' --to='new' --full src/
```

### Clean Backups

Remove backups when satisfied:
```bash
uvx repren@latest --clean-backups src/
```

## Common Workflows

### Large Codebase Refactoring

1. Preview changes:
```bash
uvx repren@latest --from='OldName' --to='NewName' --preserve-case --word-breaks --full --dry-run src/
```

2. Execute if output looks correct:
```bash
uvx repren@latest --from='OldName' --to='NewName' --preserve-case --word-breaks --full src/
```

3. Review changes, test, then clean backups:
```bash
uvx repren@latest --clean-backups src/
```

### Filtering Files

Include only specific file types:
```bash
uvx repren@latest --patterns=patterns.txt --include='.*\.(py|pyi)$' --full src/
```

Exclude directories:
```bash
uvx repren@latest --patterns=patterns.txt --exclude='tests|node_modules|__pycache__' --full src/
```

### Word Boundaries

Match only at word boundaries (safer for variable names):
```bash
uvx repren@latest --from='var' --to='variable' --word-breaks --full src/
```

### Literal Patterns

Treat patterns as literal strings (not regex):
```bash
uvx repren@latest --from='file.txt' --to='data.txt' --literal --full docs/
```

### Multi-Line Patterns

Process entire files at once for patterns spanning lines:
```bash
uvx repren@latest --patterns=patterns.txt --at-once --full src/
```

## Machine-Readable Output

Use JSON format for programmatic processing:
```bash
uvx repren@latest --format=json --from='old' --to='new' --full src/
```

Returns structured data about all changes made.

## Key Flags

Most important flags (run `uvx repren@latest --docs` for complete list):

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
