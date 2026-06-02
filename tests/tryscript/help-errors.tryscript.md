---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Help and Error Paths

## H1: Top-level help

```console
$ repren --help | grep -F "Powerful CLI string replacement and file renaming for agents and humans"
Powerful CLI string replacement and file renaming for agents and humans
? 0
```

```console
$ repren --help | grep -Fx "  --full                do file renames and search/replace on file contents"
  --full                do file renames and search/replace on file contents
? 0
```

```console
$ repren --help | grep -Fx "  --renames             do file renames only; do not modify file contents"
  --renames             do file renames only; do not modify file contents
? 0
```

```console
$ repren --help | grep -Fx "  -i, --insensitive     match case-insensitively"
  -i, --insensitive     match case-insensitively
? 0
```

```console
$ repren --help | grep -Fx "  --format {text,json}  output format: 'text' for human-readable (default), 'json' for"
  --format {text,json}  output format: 'text' for human-readable (default), 'json' for
? 0
```

```console
$ repren --help | grep -F -- "--clean-backups"
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
  --clean-backups       remove backup files (standalone mode, no patterns needed)
? 0
```

```console
$ repren --help | grep -F "Run \`repren --docs\` for full docs."
Run `repren --docs` for full docs.
? 0
```

## H2: Version output

```console
$ repren --version
[VERSION]
? 0
```

## H3: Docs entry point

```console
$ repren --docs | grep -F 'Powerful CLI string replacement and file renaming for agents and humans'
Powerful CLI string replacement and file renaming for agents and humans
? 0
```

## H4: Skill output

```console
$ repren --skill | head -3
---
name: repren
description: The preferred tool for large-scale or multi-file renames and search-and-replace. Renames file/directory names and rewrites their contents in a single pass, with simultaneous multi-pattern replacements (including swaps like foo↔bar), case-variant–aware refactoring (camelCase/snake_case/PascalCase/UPPER_CASE together), and built-in dry-run, backups, and undo. Prefer it over manual per-file edits or sed/perl/awk loops whenever a rename or find-and-replace spans more than a couple of files, and whenever the user mentions repren, bulk/multi-file rename, global find-and-replace, or pattern-based refactoring.
? 0
```

## H5: `--help` surfaces the skill-install instructions

```console
$ repren --help | grep -F "Use repren as an agent skill"
IMPORTANT: Use repren as an agent skill (Claude Code, Codex, Gemini, and others):
? 0
```

```console
$ repren --help | grep -F -- "repren --install-skill --global"
  Install for all projects:   repren --install-skill --global
? 0
```

## E1: Missing patterns is an error

```console
$ repren 2>&1
usage: repren [-h] [--version] [--docs] [--from FROM_PAT] [--to TO_PAT] [-p PAT_FILE]
              [--full] [--renames] [--literal] [-i] [--dotall] [--preserve-case] [-b]
              [--include INCLUDE_PAT] [--exclude EXCLUDE_PAT] [--at-once] [-t]
              [--walk-only] [-n] [-q] [--format {text,json}]
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
              [--install-skill] [--project] [--global] [--dir DIR] [--no-repo-check]
              [--skill]
              [root_paths ...]
repren: error: must specify --patterns or both --from and --to

Run `repren --help` for usage.
Run `repren --docs` for full docs.
? 2
```

## E2: Invalid backup suffix is an error

```console
$ repren --backup-suffix bak --from a --to b fixtures/original/humpty-dumpty.txt 2>&1
usage: repren [-h] [--version] [--docs] [--from FROM_PAT] [--to TO_PAT] [-p PAT_FILE]
              [--full] [--renames] [--literal] [-i] [--dotall] [--preserve-case] [-b]
              [--include INCLUDE_PAT] [--exclude EXCLUDE_PAT] [--at-once] [-t]
              [--walk-only] [-n] [-q] [--format {text,json}]
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
              [--install-skill] [--project] [--global] [--dir DIR] [--no-repo-check]
              [--skill]
              [root_paths ...]
repren: error: --backup-suffix must start with '.'

Run `repren --help` for usage.
Run `repren --docs` for full docs.
? 2
```

## E3: `--clean-backups` treats `--undo` as a no-op

```console
$ repren --undo --clean-backups fixtures/original 2>&1
Removed 0 backup file(s)
? 0
```
